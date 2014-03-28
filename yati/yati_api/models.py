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
#import jsonfield
import dbarray

from translate.tools import poterminology
from translate.storage import pypo, poparser
from translate.misc.multistring import multistring

from django.db import models
from django.db.models.query import Q
from django.conf import settings
from django.utils.translation import ugettext as _

#INTERFACE_LANGUAGES = sorted([(l, dict(settings.LANGUAGES)[l]) for l in settings.INTERFACE_LANGUAGES], key=lambda x: x[1])

# class Project(models.Model):
#     name = models.CharField(max_length=255)

#     def create_or_get_pofile(self, language, path=None):
#         try: return self.pofiles.get(path=path, language=language)
#         except Pofile.DoesNotExist:
#             return self.pofiles.create(path=path, language=language)

#     def import_pofile(self, language, path=None):
#         pofile = self.create_or_get_pofile(language, path)

#     def __unicode__(self):
#         return u'"%s"'%self.name

LANGUAGES = sorted(settings.LANGUAGES, key=lambda x: x[1])

class YatiException(Exception):
    pass

class Project(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'"%s"'%self.name

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

    type = models.CharField(choices=TYPE_CHOICES, default='po', max_length=100)
    project = models.ForeignKey(Project, related_name='stores')
    source = models.TextField(_('Store source (e.g. filename)'), null=True)
    sourcelanguage = models.CharField(choices=LANGUAGES, default='en', max_length=10)
    targetlanguage = models.CharField(choices=LANGUAGES, max_length=10, null=False, blank=False)
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
        return u'%s, (%s -> %s), project: %s'%(self.source, self.sourcelanguage, self.targetlanguage, self.project.name)

    def read(self):
        "Read whatever the source and return pofile"
        return getattr(self, 'read_%s'%self.type)()

    def read_po(self):
        """
        Read pofile from the disk

        Returns translate.storage.pypo.pofile instance
        """
        pofile = pypo.pofile()
        handle = open(self.source, 'r')
        pofile.parse(handle)
        handle.close()
        return pofile
    
    def read_term(self, stores=[]):
        """
        Export terminology from specified stores
        if no source specified, all the stores with same project
        and targetlanguage will be used

        Returns pypo.pofile instance with combined terminology
        """

    def update(self, pofile=False):
        """
        Update units in database with given pofile
        If no pofile passed, it will be taken from self.read()

        If pofile and database have different target strings for
        the same msgid, database version will prevail

        @TODO must check for obsolete translations and mark them as such in database
        """
        if not pofile: pofile = self.read()
        for i in xrange(len(pofile.units)):
            pounit, unit = pofile.units[i], None
            try:
                unit = self.units.get(
                    msgid=Unit.pounit_get(pounit, 'source'))
            except Unit.DoesNotExist:
                unit = Unit(store=self)
            unit.index = i
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
        for unit in self.units.exclude(index=0, msgid=['']).all().order_by('index'):
            pofile.addunit(unit.to_pounit())
        return pofile

class Unit(models.Model):
    index = models.IntegerField(null=True)
    store = models.ForeignKey(Store, related_name='units')
    msgid = dbarray.TextArrayField(default=[], null=True)
    msgstr = dbarray.TextArrayField(default=[])
    comments = models.TextField(default='')
    #last_read
    #last_write
        # unit.getnotes() returns .othercomments and .automaticcomments already concated with \n's
        # What about msgidcomments and msgid_pluralcomments ???
    #prev_msgid ???
    #@TODO unique(store, msgid) ?

    def hasplural(self):
        return len(self.msgid) > 1

    def to_pounit(self):
        return Unit.to_pypo(self)

    def from_pounit(self, pounit):
        unit = Unit.from_pypo(pounit)
        for attr in ('msgid', 'msgstr', 'comments'):
            setattr(self, attr, getattr(unit, attr))
        self.save()

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

class Location(models.Model):
    unit = models.ForeignKey(Unit, related_name='locations')
    filename = models.TextField()
    lineno = models.IntegerField()

    def __unicode__(self):
        return u'%s:%s'%(self.filename, self.lineno)

class Module(models.Model):
    """
    Group of several units matched by location pattern

    This is to be cross-language
    """
    project = models.ForeignKey(Project, related_name='modules')
    name = models.CharField(max_length=255)
    pattern = models.TextField(null=True)

    def __unicode__(self):
        return u'%s: %s (%s)'%(self.project.name, self.name, self.pattern)