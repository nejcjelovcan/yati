from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext

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
        qs = Unit.objects.all().exclude_header()
        if self.request.method == 'GET':
            module_id = self.request.GET.get('module_id')
            language = self.request.GET.get('language')
            filter = self.request.GET.get('filter')
            if not language in get_setting('LANGUAGES'):
                raise Exception("Must provide valid language parameter")
            qs = qs.filter(store__targetlanguage=language)
            if filter == 'untranslated':
                qs = qs.undone()
            if module_id:
                qs = qs.by_module(Module.objects.get(id=module_id)).order_by('id').distinct('id')
            return qs
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

@ensure_csrf_cookie
def main(request):
    return render_to_response('main.html', {}, context_instance=RequestContext(request))