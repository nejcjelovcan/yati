import os
import StringIO

from django.test import TestCase
from django.test.client import Client
from django.conf import settings

from models import Project, Store, Unit, Location, Module

#from vl.tests import _default_site, _get_user, _test_server, _create_lecture, TestClient, CLIENT_USERNAME, CLIENT_PASSWORD

PATH = os.path.dirname(os.path.realpath(__file__))

class ModelTest(TestCase):

    def setUp(self):
        self.project = Project.objects.create(name='Test')
        self.store = self.project.stores.create(source=os.path.join(PATH, 'testmedia/test.sl.po'), targetlanguage='sl')

    def testReadWritePofile(self):
        "Read and write po file, check that they're the same"
        self.store.update()

        buf = StringIO.StringIO()
        self.store.write(handle=buf)
        buf.seek(0)

        # check that files are identical!
        f = open(self.store.source, 'r')
        for line in f.readlines():
            self.assertEqual(line, buf.readline())

        f.close()

    def testModules(self):
        self.store.update()
        
        self.assertEqual(self.project.get_orphan_units().count(), Unit.objects.all().count())
        self.assertEqual(self.project.get_orphan_locations().count(), 3)

        mod = Module.objects.create(project=self.project, name='Engine', pattern='/engines/')
        self.assertEqual(mod.units.count(), 4)
        self.assertEqual(self.project.get_orphan_units().count(), Unit.objects.all().count() - mod.units.count())
        self.assertEqual(self.project.get_orphan_locations().count(), 2)


    # def testTerminology(self):
    #     self.pofile.read()
    #     self.pofile.read_terminology()

    #     self.assertItemsEqual(Term.objects.all().values_list('sid', flat=True), [u'slide'])
    #     msg = self.pofile.messages.create(sid=u'Go to next slide')
    #     self.assertItemsEqual(map(lambda t: t.sid, msg.terminology()), [u'slide'])

    # def testModules(self):
    #     self.pofile.read()
    #     self.assertEqual(len(Module.get_orphan_messages()), Message.objects.all().count())

    #     locations = Module.get_orphan_messages(locations=True)
    #     self.assertEqual(len(locations), 3)
    #     self.assertTrue(all(map(lambda l: 'smileplayer' in l, locations)))

    #     Module.objects.create(name='player', pattern='smileplayer')
    #     self.assertEqual(len(Module.get_orphan_messages()), 0)

    def tearDown(self):
        Project.objects.all().delete()
        Store.objects.all().delete()
        Unit.objects.all().delete()
