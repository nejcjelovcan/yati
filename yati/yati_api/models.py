"""
Yati models

Loosely based on translate.storage.base classes
Intented for use with pofiles, so a lot of XLIFF specifics
are omitted/concreted out

For example, there is no Context for the time being,
but we might abstract Location model and make a general
Context one that will cover other uses in XLIFF specification

Storage is also pretty pofile-specific with headers
and it only supports one source and one target language

There are no XLIFF groups, msgid_id and msgstr are JSON list fields so
that a variable number of plural sources and targets
can be provided. psql json ftw (or just textfield)

Storage and Unit models can be cast one-to-one into translate classes
pypo.pofile and pypo.pounit (which are subclasses of TranslationStore
and TranslationUnit)

Project
    has one or several Stores, each of them language specific

Store
    belongs to a project
    has source and target language
    maps to a pofile on disk - 'source' field
        (but doesn't have to - can only be "virtual" pofile in database)
    carries timing information (but headers are actually saved to unit instance with msgid [""]))
    can be cast into pypo.pofile

Unit
    is a base translation unit
    can be plural (has msgid of length > 1)
    msgstr is ALWAYS a JSON list field (only one element if not plural)
    can have several locations (comments in pofile that specify where in the source this string is originating from)
    has a comments text field where all the different pofile comments go (except locations)
    can be cast into pypo.pounit (which is a subclass of storage.base.TranslationUnit)

Location
    belongs to a specific unit
    has filename and location
    @TODO why every languages' units have their own locations

Module
    belongs to a project
    has a name
    has a string pattern that we match against Location.filename
        if matched, Location's Unit is considered under this location pattern (in this "Module")

"""

import os
import re
import json
import time
import datetime
import cStringIO

import Levenshtein
import dbarray
from model_utils.managers import PassThroughManager

from translate.tools import poterminology
from translate.storage import pypo, poparser
from translate.misc.multistring import multistring

from django.db import models
from django.db.models.query import Q
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

from settings import get_setting

class YatiException(Exception):
    pass

def q_by_languages(target=None, source=None, prefix='store__'):
    assert target or source, "Specify target our source language"
    QQ = lambda field, val: Q(**{prefix + field + 'language__in': val})
    q, q1 = None, None
    if target and type(target) not in (tuple, list): target = [target]
    if source and type(source) not in (tuple, list): source = [source]
    if target: q = QQ('target', target)
    if source: q1 = QQ('source', source)
    q = q & q1 if q and q1 else (q1 or q)
    return q

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email,
            password=password
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model (email-based with password)

    Has languages field (comma separated language codes)

    Some manager filters (e.g. Project.get_for_user)
    will filter only projects that have targetlanguages present
    in user's language field
    (unless languages==null or user.is_staff==true)
    """

    email = models.EmailField('email address', unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    languages = models.CharField(default=None, null=True, max_length=255)

    objects = UserManager()

    USERNAME_FIELD = 'email'
        
    def __unicode__(self):
        return self.email

    def is_admin():
        doc = "Alias for is_staff"
        def fget(self):
            return self.is_staff
        def fset(self, value):
            self.is_staff = value
        return locals()
    is_admin = property(**is_admin())

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_languages(self):
        if self.languages:
            return filter(bool, self.languages.split(','))
        return []

    def set_languages(self, languages):
        self.languages = ','.join(languages)+','

class ProjectQuerySet(models.query.QuerySet):
    def get_for_user(self, user):
        # @TODO also check module permissions for project ?!

        from guardian.shortcuts import get_objects_for_user
        if user.is_admin or user.has_perm('yati_api.change_project'
            or user.has_perm('yati_api.contribute_project')): return self
        qs = get_objects_for_user(user, ['yati_api.contribute_project', 'yati_api.change_project'], any_perm=True)

        langs = user.get_languages()
        if len(langs):
            qs = qs.by_language(target=langs)
        return qs

    def by_language(self, target=None, source=None):
        return self.filter(q_by_languages(target, source, prefix='stores__'))

class Project(models.Model):
    unit_manager_filter = 'by_project'

    name = models.CharField(max_length=255)

    objects = PassThroughManager.for_queryset_class(ProjectQuerySet)()

    class Meta:
        permissions = (
            ('contribute_project', 'Can contribute translations to a project'),
        )

    def __unicode__(self):
        return u'"%s"'%self.name

    def get_orphan_units(self):
        return self.get_orphan(Unit).order_by('store', 'msgid').distinct('store', 'msgid')
        
    def get_orphan_locations(self):
        return self.get_orphan(Location).order_by('filename').distinct('filename').values_list('filename', flat=True)

    def get_orphan(self, model_cls, query=False):
        q = None
        qs = model_cls.objects.all()
        for module in self.modules.exclude(pattern=None):
            q1 = qs.by_module(module, query=True)
            q = q | q1 if q else q1
        if query: return ~q if q else Q()
        if q: return qs.exclude(q)
        return qs

    @property
    def units(self):
        return Unit.objects.exclude_terminology().by_project(self).order_by('id').distinct('id')

    @property
    def targetlanguages(self):
        return self.stores.values_list('targetlanguage', flat=True).distinct()

    def save(self, *args, **kwargs):
        result = super(Project, self).save(*args, **kwargs)

        # create uncategorized module
        if not self.modules.filter(pattern=None).exists():
            self.modules.create(name='Uncategorized', pattern=None)

        return result

    def get_terminology_store(self, targetlanguage):
        "Returns terminology store"
        try: return self.stores.get(targetlanguage=targetlanguage, type='term')
        except Store.DoesNotExist: return Store(project=self, targetlanguage=targetlanguage, type='term')

    def get_terminology(self, query, targetlanguage):
        # @TODO some kind of auto updating mechanism?
        return self.get_terminology_store(targetlanguage).units.all().by_msgid_levens(query)

# class ProjectUserObjectPermission(UserObjectPermissionBase):
#     content_object = models.ForeignKey(Project)

class Store(models.Model):
    """
    Store

    This is mainly used as a Pofile abstraction,
    but also as a virtual Terminology Pofile
    (one per project/language expected)

    @TODO support dynamic files (e.g. no source means pofile can be found somwhere under 'id'.po)
    @TODO actually reconsider if source should ever be used for anything else than remembering uploaded filename
    """

    TYPE_CHOICES = (
        ('po', 'PO file'),
        ('term', 'Terminology')
    )

    RE_CLEARTERM = re.compile(r'{[^}]*}')   # used to clear termninology strings

    type = models.CharField(choices=TYPE_CHOICES, default='po', max_length=100)
    project = models.ForeignKey(Project, related_name='stores')
    filename = models.TextField(_('Filename'))  # just for info
    sourcelanguage = models.CharField(choices=settings.LANGUAGES, default='en', max_length=10)
    targetlanguage = models.CharField(choices=settings.LANGUAGES, max_length=10, null=False, blank=False)

    def __unicode__(self):
        return u'%s, (%s -> %s), project: %s'%(self.getDirname() if self.type == 'po' else 'TERMINOLOGY', self.sourcelanguage, self.targetlanguage, self.project.name)

    @property
    def header(self):
        try: return self.units.get(index=0, msgid=[''])
        except Unit.DoesNotExist: pass

    @property
    def headers(self):
        if self.header:
            pofile = pypo.pofile()
            pofile.units = [self.header.to_pounit()]
            return pofile.parseheader()
        return {}

    @property
    def lastExport(self):
        try: last_export = self.logs.filter(event='export').order_by('-time')[0].time
        except IndexError: pass

    @property
    def lastImport(self):
        try: last_export = self.logs.filter(event='import').order_by('-time')[0].time
        except IndexError: pass

    def getDirname(self):
        assert self.type == 'po'
        # @TODO unix folder limits
        return os.path.join(get_setting('STORE_PATH'), str(self.id))

    def getFilename(self, path):
        return os.path.join(self.getDirname(), path)

    def read(self, path=None):
        """
        Read pofile from the disk

        Returns translate.storage.pypo.pofile instance
        """
        assert self.type == 'po'
        pofile = pypo.pofile()
        handle = open(path or self.getFilename('import.po'), 'r')
        pofile.parse(handle)
        handle.close()
        return pofile

    def update(self, *args, **kwargs):
        return getattr(self, 'update_%s'%self.type)(*args, **kwargs)

    def update_term(self, stores=None, user=None):
        """
        Export terminology from specified stores
        and update units in this store
        if no source specified, all the stores with same project
        and targetlanguage will be used
        """
        assert self.type == 'term'
        if not stores:
            stores = list(self.project.stores.filter(targetlanguage=self.targetlanguage, type='po'))

        if len(stores) > 0:
            tex = poterminology.TerminologyExtractor()

            for store in stores:
                pof = store.to_pofile()
                tex.processunits(pof.units, 'Store %s'%store.id)

            terminology = tex.extract_terms()
            i = 0
            for item in sorted(terminology.values(), key=lambda t: t[0], reverse=True):
                source = Unit.pounit_get(item[1], 'source')
                strings = filter(lambda s: bool(s), map(unicode.strip, self.RE_CLEARTERM.sub('', unicode(item[1].gettarget())).split(';')))

                if source and len(strings) > 0:
                    unit = None
                    try: unit = self.units.get(msgid=source)
                    except Unit.DoesNotExist: unit = Unit(store=self)
                    unit.index = i
                    unit.msgid = source
                    unit.msgstr = strings
                    # item[1].getlocations() @TODO whenever we need this...
                    unit.save()

                i += 1

        self.logs.create(user=user, event='import', 
            data='Stores: %s'%(','.join(map(lambda s: str(s.id), stores))))

    def update_po(self, pofile=False, user=None, data=None, overwrite='time'):
        """
        Update units in database with given pofile
        If no pofile passed, it will be taken from self.read()

        If unit is already found in database (has same msgid)
        times will be checked. If store was exported after
        user change was done to the unit, it will be overwritten,
        otherwise 

        overwrite options:
        'never' or False        never overwrite database translations
        'time' or None          overwrite database translations if store export happened after unit user change
        'always' or True        always overwrite

        @TODO backup store before importing
        """
        # backup, first (unless no units)
        if self.units.all().exists():
            self.write(fn=self.getFilename('backup_%s.po'%time.time()))

        # determine pofile (default [store_path]/[id]/import.po)
        if isinstance(pofile, basestring):
            if not data: data = pofile
            pofile = self.read(pofile)
        elif not pofile:
            if not data: data = self.getFilename('import.po')
            pofile = self.read()

        # resolve overwrite rule
        if overwrite == None: overwrite = 'time'
        elif overwrite == True: overwrite = 'always'
        elif overwrite == False: overwrite = 'never'
        assert overwrite in ('time', 'always', 'never')

        # remember updated unit ids so that we know which are obsolete
        # @TODO better way
        unit_ids = list(self.units.exclude(obsolete=True).values_list('id', flat=True))
        for i in xrange(len(pofile.units)):
            pounit = pofile.units[i]
            unit, new, update = None, False, overwrite == 'always'
            try:
                unit = self.units.get(msgid=Unit.pounit_get(pounit, 'source'))
                if overwrite == 'time':
                    if not self.lastExport or not unit.lastChange: update = True
                    elif self.lastExport > unit.lastChange: update = True
                    elif unit.pounit_msgstr_equals(pounit): update = True
                elif overwrite == 'never': update = False
            except Unit.DoesNotExist:
                new, update = True, True
                unit = Unit(store=self)
            if update:
                unit.index = i  # @TODO ?
                unit.obsolete = False
                unit.from_pounit(pounit, event=('import_new' if new else 'import', ''), user=user)

            if unit.id in unit_ids: unit_ids.remove(unit.id)

        # go through unit id's that are left over and mark them as obsolete
        # @TODO better way (we have logs!)
        for i in range(len(unit_ids)/10 + 1):
            ids = unit_ids[i*10:i*10+10]
            for unit in Unit.objects.filter(id__in=ids):
                unit.obsolete = True
                unit.save(user=user, event='obsolete')

        self.logs.create(user=user, event='import', data=data)

    def write(self, fn=None, handle=None, user=None, data=None, log=False):
        """
        Write the actual pofile to the disk (or given handle)

        If log is false (which is default), no log will be written
        (useful if write will not result in source update
        since units can be marked as changed after last export)
        @TODO confusing but should be handled by API
            for the usual use cases
        """
        if self.type == 'term' and not handle: raise YatiException('Specify handle when writing terminology store')
        if not handle:
            if not fn:
                fn = self.getFilename('export_%s.po'%time.time())
            if not data: data = fn
            handle = open(fn, 'w')

        pofile = self.to_pofile()
        handle.write(str(pofile))
        if log:
            self.logs.create(user=user, event='export', data=data)
        return fn

    def to_pofile(self, pofile=None):
        """
        Export from database to (given or newly instantiated) pofile
        Headers are only set on pofile if no pofile was passed !!!
        """
        if not pofile:
            pofile = pypo.pofile()
            pofile.settargetlanguage(self.targetlanguage)
            if self.header:
                pofile.units = [self.header.to_pounit()]
        for unit in self.units.exclude_header().order_by('index'):
            pofile.addunit(unit.to_pounit())
        return pofile

    def save(self, *args, **kwargs):
        if self.type == 'po' and not self.targetlanguage:
            try:
                pof = self.read()
                self.targetlanguage = pof.gettargetlanguage()
            except:
                self.targetlanguage = None
        super(Store, self).save(*args, **kwargs)

class UnitQuerySet(models.query.QuerySet):
    def by_module(self, module, exclude=False, query=False):
        """
        Warning: this can return duplicate units
        use e.g. .order_by('id').distinct('id')
        """
        q = None
        if module.pattern: q = Q(store__project=module.project, locations__filename__icontains=module.pattern)
        else: q = module.project.get_orphan(Unit, query=True)   # @TODO get_orphan already has store__project in every OR
        if exclude: q = ~q
        if query: return q
        return self.filter(q)

    def by_project(self, project):
        return self.filter(store__project=project)

    def by_language(self, target=None, source=None):
        return self.filter(q_by_languages(target, source, prefix='store__'))

    def exclude_header(self):
        return self.exclude(index=0, msgid=[''])

    def exclude_terminology(self):
        return self.exclude(store__type='term')

    def q_done(self):
        return Q(msgid=[''])|~(Q(msgstr=[''])|Q(msgstr=['','']))

    def done(self):
        # @TODO check plurals according to language
        return self.filter(self.q_done())

    def undone(self):
        return self.exclude(self.q_done())

    def by_msgid_levens(self, query):
        query = unicode(query)
        lswhere = []
        terms = filter(lambda s: not not s, map(lambda s: s.strip(' \n\t.,:.\'"'), query.split(' ')))
        for i in range(len(terms) - 1):
            if len(terms[i]) < 2 or len(terms[i+1]) < 2: continue
            lswhere.append(u'%s %s'%(terms[i], terms[i+1]))

        lswhere += filter(lambda s: len(s) > 3, terms)
        lswhere = map(unicode.lower, lswhere)

        if len(lswhere):
            # interesting fact: postgresql array are 1-indexed (not 0-indexed)
            qs = self.filter(store__type='term')\
                .extra(where=[' OR '.join(['levenshtein(lower(yati_api_unit.msgid[1]), %s) < char_length(yati_api_unit.msgid[1])/3']*len(lswhere))], params=lswhere)
            return sorted(qs, key=lambda u: UnitQuerySet.ls_score(u, lswhere))

        return []

    @staticmethod
    def ls_score(unit, lswhere):
        min = 99
        for s in lswhere:
            l = ((float(Levenshtein.distance(unit.msgid[0].lower(), s))/len(unit.msgid[0])) or 0.01)
            if l < min: min = l
        return min/(float(len(unit.msgid[0]))/100)

class Unit(models.Model):
    index = models.IntegerField(null=True)
    store = models.ForeignKey(Store, related_name='units')
    msgid = dbarray.TextArrayField(default=[], null=True)
    msgstr = dbarray.TextArrayField(default=[])
    comments = models.TextField(default='')
    fuzzy = models.BooleanField(default=False)
    obsolete = models.BooleanField(default=False)

    # @TODO unique(store, msgid) ? -- this is respected upon imports so we should make it a DB constraint

    objects = PassThroughManager.for_queryset_class(UnitQuerySet)()

    def hasplural(self):
        return len(self.msgid) > 1

    def to_pounit(self):
        return Unit.to_pypo(self)

    def from_pounit(self, pounit, user=None, event=None):
        unit = Unit.from_pypo(pounit)
        for attr in ('msgid', 'msgstr', 'comments'):
            setattr(self, attr, getattr(unit, attr))
        self.fuzzy = pounit.isfuzzy()
        self.save(event=event, user=user)
        self.locations.all().delete()
        for location in pounit.getlocations():
            fn, lineno = location.split(':')
            self.locations.create(filename=fn, lineno=lineno)

    @property
    def lastChange(self):
        try: self.logs.filter(type='change').order_by('-time')[0].time
        except IndexError: return None

    def __unicode__(self):
        if self.hasplural():
            mp = lambda ss: ', '.join(['"%s"'%s for s in ss])
            return u'%s: %s'%(mp(self.msgid), mp(self.msgstr))
        else: return u'%s: %s'%(self.msgid[0], self.msgstr[0])

    class Meta:
        ordering = ('store', 'index')

    @staticmethod
    def to_pypo(unit):
        pounit = pypo.pounit(source=multistring(unit.msgid) if unit.hasplural() else (unit.msgid[0] if len(unit.msgid) else ''))
        pounit.target = multistring(unit.msgstr) if unit.hasplural() else unit.msgstr[0]

        if unit.comments:
            ps = poparser.ParseState(cStringIO.StringIO(unit.comments.encode('utf8')),
                pypo.pounit,
                encoding='utf-8')
            poparser.parse_comments(ps, pounit)

        return pounit

    @staticmethod
    def from_pypo(pounit, unit=False):
        unit = Unit(
            msgid=Unit.pounit_get(pounit, 'source'),
            msgstr=Unit.pounit_get(pounit, 'target'),
            comments=''.join([comment for comments in pounit.allcomments for comment in comments]))
            #         :D ^^
            # @SEE http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        return unit

    @staticmethod
    def pounit_get(pounit, attr='source'):
        if attr == 'source' and pounit.source == []: return None
        return map(unicode, getattr(pounit, attr).strings if pounit.hasplural() else [getattr(pounit, attr)])

    def pounit_msgstr_equals(self, pounit):
        target = Unit.pounit_get(pounit, 'target')
        if len(target) != len(self.msgstr): return False
        for i in range(len(pounit.msgstr)):
            if target[i] != self.msgstr[i]: return False
        return True

    def save(self, *args, **kwargs):
        event = kwargs.pop('event', None)
        user = kwargs.pop('user', None)
        # assert event and user @TODO
        result = super(Unit, self).save(*args, **kwargs)
        if event:
            if type(event) in (list, tuple):
                try: data = event[1]
                except IndexError: pass
                event = event[0]
            self.logs.create(user=user, event=event, data=data)
        return result

STORE_LOG_EVENTS = (
    ('import', 'Imported pofile'),
    ('export', 'Exported pofile'),
    ('term', 'Collected terminology'),
)

UNIT_LOG_EVENTS = (
    ('import', 'Unit was imported'),
    ('import_new', 'Unit was newly imported'),
    #('import_ignore', 'Unit should be imported but was changed in the database')
    ('change', 'Unit was changed by user'),
    ('obsolete', 'Unit was marked as obsolete'),
)

class AbstractLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    data = models.TextField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)   # @TODO null=true???

    class Meta:
        abstract = True

class StoreLog(AbstractLog):
    store = models.ForeignKey(Store, related_name='logs')
    event = models.CharField(max_length=255, choices=STORE_LOG_EVENTS)

    def __unicode__(self):
        return '[%s] (%s) %s: %s'%(self.time.isoformat(), self.user, dict(STORE_LOG_EVENTS)[self.event], self.data)

class UnitLog(AbstractLog):
    unit = models.ForeignKey(Unit, related_name='logs')
    event = models.CharField(max_length=255, choices=UNIT_LOG_EVENTS)

    def __unicode__(self):
        return '[%s] (%s) %s: %s'%(self.time.isoformat(), self.user, dict(UNIT_LOG_EVENTS)[self.event], self.data)

class LocationQuerySet(models.query.QuerySet):
    def distinct_filenames(self):
        return self.distinct('filename').order_by('filename').values_list('filename', flat=True)

    def by_module(self, module, exclude=False, query=False):
        q = Q(
            unit__store__project=module.project,
            filename__icontains=module.pattern
        )
        if exclude: q = ~q
        if query: return q
        return self.filter(q)

class Location(models.Model):
    unit = models.ForeignKey(Unit, related_name='locations')
    filename = models.TextField()
    lineno = models.IntegerField()

    objects = PassThroughManager.for_queryset_class(LocationQuerySet)()

    def __unicode__(self):
        return u'%s:%s'%(self.filename, self.lineno)

class ModuleQuerySet(models.query.QuerySet):
    def get_for_user(self, user):   # @TODO also check module permissions for project ?!
        "Warning: this resets the queryset chain"
        from guardian.shortcuts import get_objects_for_user
        if user.is_admin or user.has_perm('yati_api.change_module'
            or user.has_perm('yati_api.contribute_module')): return self
        return get_objects_for_user(user, ['yati_api.contribute_module', 'yati_api.change_module'], any_perm=True)

    def get_for_unit(self, unit):
        "Reverse for UnitQuerySet.by_model @1337 @TODO test"
        ors = []
        for location in unit.locations.all().values_list('filename', flat=True):
            ors.append(('%s LIKE %s || pattern',  (location.filename, '%')))
        return self.filter(project=unit.store.project)\
            .extra(
                where=[' OR '.join(map(lambda p: p[0], ors))],
                params=reduce(tuple.__add__, map(lambda p: p[1], ors), ())
            )

class Module(models.Model):
    """
    Group of several units matched by location pattern

    This is to be cross-language
    """
    unit_manager_filter = 'by_module'

    project = models.ForeignKey(Project, related_name='modules')
    name = models.CharField(max_length=255)
    pattern = models.TextField(null=True)   # null pattern means units with no location will be matched

    objects = PassThroughManager.for_queryset_class(ModuleQuerySet)()

    @property
    def units(self):
        return Unit.objects.all().exclude_terminology().by_module(self).order_by('id').distinct('id')

    class Meta:
        permissions = (
            ('contribute_module', 'Can contribute translations to module'),
        )

    def __unicode__(self):
        return u'%s: %s (%s)'%(self.project.name, self.name, self.pattern)
