from django.shortcuts import render_to_response
from django.conf import settings

from rest_framework import viewsets

import serializers
from models import Project, Store, Unit, Module, Location
from yati_api.settings import get_setting

LANGUAGES = dict(sorted(settings.LANGUAGES, key=lambda x: x[1]))

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()

    def get_queryset(self):
        language = self.request.GET.get('language')
        qs = Project.objects.all()
        if language: qs = qs.filter(stores__targetlanguage=language).distinct('id')
        return qs

class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StoreSerializer
    queryset = Store.objects.all()

class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UnitSerializer
    queryset = Unit.objects.all()

    def get_queryset(self):
        module_id = self.request.GET.get('module_id')
        language = self.request.GET.get('language')
        if not language in map(lambda l: l[0], LANGUAGES):
            raise Exception("Must provide language parameter")
        qs = Unit.objects.all().filter(store__targetlanguage=language)
        if module_id:
            qs = qs.by_module(Module.objects.get(id=module_id))
        return qs

# Mock model and queryset for language
# this is fugly @TODO
class Language(dict):
    @property
    def id(self): return self.get('id')

    @property
    def display(self): return self.get('display')

class LanguageQueryset(list):
    def _clone(self):
        import copy
        return copy.copy(self)

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LanguageSerializer
    queryset = LanguageQueryset([Language(id=item, display=LANGUAGES[item]) for item in get_setting('LANGUAGES')])
    paginate_by = 500

def main(request):
    return render_to_response('main.html')