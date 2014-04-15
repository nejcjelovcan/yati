import os
import StringIO

from django.test import TestCase
from django.test.client import Client
from django.conf import settings

from models import Project, Store, Unit, Location, Module, StoreLog, UnitLog

#from vl.tests import _default_site, _get_user, _test_server, _create_lecture, TestClient, CLIENT_USERNAME, CLIENT_PASSWORD

PATH = os.path.dirname(os.path.realpath(__file__))

class ModelTest(TestCase):

    def setUp(self):
        self.project = Project.objects.create(name='Test')
        self.store = self.project.stores.create(filename='test.po', targetlanguage='sl')
        self.importfile = os.path.join(PATH, 'testmedia/test.sl.po')

    def testReadWritePofile(self):
        "Read and write po file, check that they're the same"
        self.store.update(self.importfile)

        buf = StringIO.StringIO()
        self.store.write(handle=buf)
        buf.seek(0)

        # check that files are identical!
        f = open(self.importfile, 'r')
        for line in f.readlines():
            self.assertEqual(line, buf.readline())

        f.close()

    def testModules(self):
        self.store.update(self.importfile)
        
        self.assertEqual(self.project.get_orphan_units().count(), Unit.objects.all().count())
        self.assertEqual(self.project.get_orphan_locations().count(), 3)

        mod = Module.objects.create(project=self.project, name='Engine', pattern='/engines/')
        self.assertEqual(mod.units.count(), 4)
        self.assertEqual(self.project.get_orphan_units().count(), Unit.objects.all().count() - mod.units.count())
        self.assertEqual(self.project.get_orphan_locations().count(), 2)

        self.assertEqual(Unit.objects.by_module(mod).distinct('msgid').count() +
            Unit.objects.by_module(self.project.modules.get(name='Uncategorized')).distinct('msgid').count(),
            Unit.objects.all().count())

    def testTerminology(self):
        self.store.update(self.importfile)
        units = self.project.units.all().count()

        term = self.project.get_terminology_store('sl')
        term.save()
        term.update()

        self.assertEqual(term.units.all().count(), 1)
        unit = term.units.all()[0]
        self.assertEqual(unit.msgid[0], 'slide')
        self.assertEqual(unit.msgstr[0], 'prosojnica')

        units = self.project.get_terminology('test slide', 'sl')
        self.assertEqual(unit.msgid[0], 'slide')
        self.assertEqual(unit.msgstr[0], 'prosojnica')

    def tearDown(self):
        Project.objects.all().delete()
        Store.objects.all().delete()
        Unit.objects.all().delete()
