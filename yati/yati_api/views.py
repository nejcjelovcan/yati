from django.shortcuts import render_to_response

from rest_framework import viewsets

import serializers
from models import Project, Store, Unit, Module, Location, LANGUAGES

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()

class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StoreSerializer
    queryset = Store.objects.all()

class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UnitSerializer
    queryset = Unit.objects.all()

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
    queryset = LanguageQueryset([Language(id=item[0], display=item[1]) for item in LANGUAGES])
    paginate_by = 500

def main(request):
    return render_to_response('main.html')