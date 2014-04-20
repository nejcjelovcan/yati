import os
import StringIO
import json

from django.test import TestCase
from django.test.client import Client
from django.conf import settings

from models import Project, Store, Unit, Location, Module, StoreLog, UnitLog, User

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


class ApiTest(TestCase):

    def _jsonGet(self, *args, **kwargs):
        return json.loads(self.client.get(*args, **kwargs).content)

    def setUp(self):
        self.project = Project.objects.create(name='Test')
        self.project2 = Project.objects.create(name='Test 2')
        self.store = self.project.stores.create(filename='test.po', targetlanguage='sl')
        self.importfile = os.path.join(PATH, 'testmedia/test.sl.po')
        self.store.update(self.importfile)

        self.admin = User.objects.create_user(email='nejc@example.com', password='test')
        self.admin.is_staff = True
        self.admin.save()

        self.user = User.objects.create_user(email='stefka@example.com', password='test')

        self.client = Client()

    def testBasicPermissions(self):
        response = self._jsonGet('/yati/projects/')
        self.assertEqual(response.get('detail'), 'Authentication credentials were not provided.')

        self.client.login(email='nejc@example.com', password='test')
        response = self._jsonGet('/yati/projects/')
        self.assertEqual(response.get('count'), 2)

        self.client.logout()
        self.client.login(email='stefka@example.com', password='test')
        response = self._jsonGet('/yati/projects/')
        self.assertEqual(response.get('count'), 0)

        from guardian.shortcuts import assign_perm
        assign_perm('contribute_project', self.user, self.project)

        response = self._jsonGet('/yati/projects/')
        self.assertEqual(response.get('count'), 1)

    def tearDown(self):
        Project.objects.all().delete()
        Store.objects.all().delete()
        Unit.objects.all().delete()
        User.objects.all().delete()