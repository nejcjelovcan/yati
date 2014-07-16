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

    #def _jsonPost(self, *args, **kwargs):
    #    return json.dumps(self.client.post(*args, **kwargs).content)

    def setUp(self):
        self.project = Project.objects.create(name='Test')
        self.project2 = Project.objects.create(name='Test 2')
        self.store = self.project.stores.create(filename='test.po', targetlanguage='sl')
        self.importfile = os.path.join(PATH, 'testmedia/test.sl.po')
        self.store.update(self.importfile)

        self.admin = User.objects.create_user(email='nejc@example.com', password='test')
        self.admin.is_staff = True
        self.admin.is_active = True
        self.admin.save()

        self.user = User.objects.create_user(email='stefka@example.com', password='test')
        self.user.is_active = True
        self.user.save()

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

    def testInviteUser(self):
        self.client.login(email='nejc@example.com', password='test')

        def post(data):
            response = self.client.post('/yati/users/', data)
            data = json.loads(response.content)
            return response, data

        response, data = post(dict())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data.get('email')[0], u'Enter a valid email address.')

        response, data = post(dict(email='nejc@example.com'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data.get('email')[0], u'User with this email already exists')

        response, data = post(dict(email='someone@example.com', language='sl'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(not not data.get('invite_token'))

        # try to login via invite
        # @TODO

    def tearDown(self):
        Project.objects.all().delete()
        Store.objects.all().delete()
        Unit.objects.all().delete()
        User.objects.all().delete()


class LoggingTest(TestCase):

    def _jsonGet(self, *args, **kwargs):
        return json.loads(self.client.get(*args, **kwargs).content)

    def _jsonPut(self, url, data):
        return json.loads(self.client.put(url, json.dumps(data), content_type="application/json").content)

    def setUp(self):
        self.project = Project.objects.create(name='Test')
        self.project2 = Project.objects.create(name='Test 2')
        self.store = self.project.stores.create(filename='test.po', targetlanguage='sl')
        self.importfile = os.path.join(PATH, 'testmedia/test.sl.po')
        self.importfile2 = os.path.join(PATH, 'testmedia/test2.sl.po')

        self.admin = User.objects.create_user(email='nejc@example.com', password='test')
        self.admin.is_staff = True
        self.admin.is_active = True
        self.admin.save()

        self.client = Client()

    def testImportExportChange(self):
        self.store.update(self.importfile)

        # check import log
        self.assertItemsEqual(self.store.logs.values_list('event', flat=True), [u'import'])

        # change unit
        self.client.login(email='nejc@example.com', password='test')
        unit = self.store.units.all().exclude_header()[0]
        response = self._jsonPut('/yati/units/%s/'%unit.id, dict(msgstr=['New text']))
        unit = Unit.objects.get(id=unit.id)
        self.assertEqual(unit.msgstr[0], 'New text')

        # check user-changed unit logs
        self.assertItemsEqual(unit.logs.all().order_by('-time').values('event', 'user'),
            [dict(event='change', user=self.admin.id), dict(event='import_new', user=None)])

        # check non-changed unit logs
        unit4 = self.store.units.all().exclude_header()[4]
        self.assertItemsEqual(unit4.logs.all().order_by('-time').values('event', 'user'),
            [dict(event='import_new', user=None)])

        # import file again
        self.store.update(self.importfile2, backup=False)

        # translation was left alone since 
        unit = Unit.objects.get(id=unit.id)
        self.assertEqual(unit.msgstr[0], 'New text')
        self.assertItemsEqual(unit.logs.all().order_by('-time').values('event', 'user'),
            [dict(event='change', user=self.admin.id), dict(event='import_new', user=None)])

        unit4 = Unit.objects.get(id=unit4.id)
        self.assertEqual(unit4.msgstr[0], 'TESTING CHANGED TRANSLATION')
        self.assertItemsEqual(unit4.logs.all().order_by('-time').values('event', 'user'),
            [dict(event='import', user=None), dict(event='import_new', user=None)])

        # @TODO check pofile headers for time changes ?
        # @TODO test other import modes ('always' and 'never')
        # @TODO export and then import again!


    def tearDown(self):
        Project.objects.all().delete()
        Store.objects.all().delete()
        Unit.objects.all().delete()
        User.objects.all().delete()