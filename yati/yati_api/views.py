from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

from rest_framework import viewsets, response, permissions

import serializers
from models import Project, Store, Unit, Module, Location
from yati_api.settings import get_setting

LANGUAGES = dict(sorted(settings.LANGUAGES, key=lambda x: x[1]))

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return Project.objects.all().get_for_user(self.request.user).distinct('id')

    #def get_queryset(self):
    #    language = self.request.GET.get('language')
    #    qs = Project.objects.all()
    #    if language: qs = qs.filter(stores__targetlanguage=language).distinct('id')
    #    return qs

# class StoreViewSet(viewsets.ModelViewSet):
#     serializer_class = serializers.StoreSerializer
#     queryset = Store.objects.all()

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()

    def get_queryset(self):
        qs = Unit.objects.all().exclude_header().exclude_terminology()
        if self.request.method == 'GET':
            module_id = self.request.GET.get('module_id')
            language = self.request.GET.get('language')
            filter = self.request.GET.get('filter')
            if not language in LANGUAGES:
                raise Exception("Must provide valid language parameter")
            qs = qs.filter(store__targetlanguage=language)
            if filter == 'untranslated':
                qs = qs.undone()
            elif filter == 'translated':
                qs = qs.done()
            if module_id:
                qs = qs.by_module(Module.objects.get(id=module_id)).order_by('id').distinct('id')
            return qs
        return qs

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.UnitSerializer
        return serializers.UnitWritableSerializer

class TermViewSet(viewsets.ViewSet):
    """
    Terminology viewset
    project_id and language (target language) are required
    if unit_id is present, Unit's msgid[0] will be used as query
    (otherwise, q parameter is expected)
    lookups are done for words with length min 3 characters
    """

    def list(self, request):
        project_id = request.GET.get('project_id')
        lang = request.GET.get('language')      # target language
        q = request.GET.get('q')                # levenshtein query
        # if unit_id is present, Unit's msgid[0] will be used as query
        unit_id = request.GET.get('unit_id')

        if unit_id:
            unit = Unit.objects.get(id=unit_id)
            q = unit.msgid[0]

        if not lang in LANGUAGES:
            raise Exception("Must provide valid language parameter")

        prj = Project.objects.get(id=project_id) # @TODO does not exist
        serializer = serializers.UnitTermSerializer(prj.get_terminology(q, lang), many=True)
        return response.Response(serializer.data)

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
    queryset = LanguageQueryset(sorted([Language(id=item, display=LANGUAGES[item]) for item in LANGUAGES], key=lambda l: l.get('id')))
    permission_classes = (permissions.AllowAny,)    # this is bad, but we're read only
    paginate_by = 500

@ensure_csrf_cookie
def main(request):
    data = dict()
    if request.user.is_anonymous:
        post = request.method=='POST'
        form = AuthenticationForm(data=request.POST if post else None)
        if post and form.is_valid():
            login(request, form.user_cache)
        else: data['login_form'] = form

    return render_to_response('main.html', data, context_instance=RequestContext(request))
