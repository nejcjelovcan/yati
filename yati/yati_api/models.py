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
import dateutil
import datetime
import StringIO

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

class YatiException(Exception):
    pass

class Project(models.Model):
    unit_manager_filter = 'by_project'

    name = models.CharField(max_length=255)

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

class Store(models.Model):
    """
    Store

    This is mainly used as a Pofile abstraction,
    but also as a virtual Terminology Pofile
    (one per project/language expected)
    """

    TYPE_CHOICES = (
        ('po', 'PO file'),
        ('term', 'Terminology')
    )

    RE_CLEARTERM = re.compile(r'{[^}]*}')   # used to clear termninology strings

    type = models.CharField(choices=TYPE_CHOICES, default='po', max_length=100)
    project = models.ForeignKey(Project, related_name='stores')
    source = models.TextField(_('Store source (e.g. filename)'), null=True)
    sourcelanguage = models.CharField(choices=settings.LANGUAGES, default='en', max_length=10)
    targetlanguage = models.CharField(choices=settings.LANGUAGES, max_length=10, null=False, blank=False)
    last_read = models.DateTimeField(_('Last read time'), blank=True, null=True)
    last_write = models.DateTimeField(_('Last write time'), blank=True, null=True)

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

    def __unicode__(self):
        return u'%s, (%s -> %s), project: %s'%(self.source if self.type == 'po' else 'TERMINOLOGY', self.sourcelanguage, self.targetlanguage, self.project.name)

    def read(self, path=None):
        """
        Read pofile from the disk

        Returns translate.storage.pypo.pofile instance
        """
        assert self.type == 'po'
        pofile = pypo.pofile()
        handle = open(path or self.source, 'r')
        pofile.parse(handle)
        handle.close()
        return pofile
        
    def update(self):    
        return getattr(self, 'update_%s'%self.type)()

    def update_term(self, stores=None):
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
                pof = store.read()
                tex.processunits(pof.units, store.source)

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

    def update_po(self, pofile=False):
        """
        Update units in database with given pofile
        If no pofile passed, it will be taken from self.read()

        If pofile and database have different target strings for
        the same msgid, database version will prevail

        @TODO must check for obsolete translations and mark them as such in database
        """
        if not pofile: pofile = self.read()
        for i in xrange(len(pofile.units)):
            pounit = pofile.units[i]
            unit = None
            try:
                unit = self.units.get(msgid=Unit.pounit_get(pounit, 'source'))
            except Unit.DoesNotExist:
                unit = Unit(store=self)
            unit.index = i  # @TODO ?
            unit.from_pounit(pounit)

    def write(self, handle=None):
        """
        Write the actual pofile to the disk (or given handle)
        """
        if not handle:
            if self.type == 'term': raise YatiException('Specify handle when writing terminology store')
            handle = open(self.source, 'w')

        pofile = self.to_pofile()
        handle.write(str(pofile))

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
        use e.g. .order_by('msgid').distinct('msgid')
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
        assert target or source, "Specify target our source language"
        q, q1 = None, None
        if target: q = Q(store__targetlanguage=target)
        if source: q1 = Q(store__sourcelanguage=source)
        q = q & q1 if q and q1 else (q1 or q)
        return self.filter(q)

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
    #last_read
    #last_write
    #prev_msgid ???
    #@TODO unique(store, msgid) ?

    objects = PassThroughManager.for_queryset_class(UnitQuerySet)()

    def hasplural(self):
        return len(self.msgid) > 1

    def to_pounit(self):
        return Unit.to_pypo(self)

    def from_pounit(self, pounit):
        unit = Unit.from_pypo(pounit)
        for attr in ('msgid', 'msgstr', 'comments'):
            setattr(self, attr, getattr(unit, attr))
        self.save()
        self.locations.all().delete()
        for location in pounit.getlocations():
            fn, lineno = location.split(':')
            self.locations.create(filename=fn, lineno=lineno)

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

        # comments @TODO unicode->str happens here just like that
        if unit.comments:
            ps = poparser.ParseState(StringIO.StringIO(str(unit.comments)),
                pypo.pounit)
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

class Module(models.Model):
    """
    Group of several units matched by location pattern

    This is to be cross-language
    """
    unit_manager_filter = 'by_module'

    project = models.ForeignKey(Project, related_name='modules')
    name = models.CharField(max_length=255)
    pattern = models.TextField(null=True)   # null pattern means units with no location will be matched

    @property
    def units(self):
        return Unit.objects.all().exclude_terminology().by_module(self).order_by('index').distinct('index')

    def __unicode__(self):
        return u'%s: %s (%s)'%(self.project.name, self.name, self.pattern)


"""
[{'id': 2, 'name': u'Custom VLN', 'description': None, 'pattern': u'_custom/vln/'},
 {'id': 4, 'name': u'Video player', 'description': None, 'pattern': u'/smileplayer/'},
 {'id': 3, 'name': u'Janitor', 'description': None, 'pattern': u'janitor/'},
 {'id': 6, 'name': u'Mailing', 'description': None, 'pattern': u'mailing/'},
 {'id': 7, 'name': u'Campaigns', 'description': None, 'pattern': u'campaigns/'},
 {'id': 5, 'name': u'Registration', 'description': None, 'pattern': u'/registration'},
 {'id': 8, 'name': u'Payments', 'description': None, 'pattern': u'payments/'},
 {'id': 9, 'name': u'Views', 'description': None, 'pattern': u'vl/;api/;attachments/;authviidea/;categories/;jobs/;permissions/;statistics/'}]
"""