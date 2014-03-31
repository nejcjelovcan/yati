import json

from django import forms
from django.utils.translation import ugettext as _

from rest_framework import serializers, fields

from models import Project, Store, Unit, Location, Module

class ArrayField(fields.CharField):
    """
    Array field for Unit.msgid and Unit.msgstr
    
    @TODO this is read-only and defaults to "" instead of []
    """
    type_name = 'ArrayField'
    type_label = 'list'
    form_field_class = forms.CharField
    widget = forms.Textarea

    def from_native(self, value):
        if isinstance(value, six.string_types) or value is None:
            return value
        return json.dumps(value)

class UnitSetCounts(object):
    def get_count(self, model):
        return [model.units.count(), model.units.done().count()]

class ModuleSerializer(serializers.ModelSerializer, UnitSetCounts):
    class Meta:
        model = Module
        fields = ('id', 'name', 'pattern', 'units_count')

    units_count = serializers.SerializerMethodField('get_count')


class ProjectSerializer(serializers.ModelSerializer, UnitSetCounts):
    class Meta:
        model = Project
        fields = ('id', 'name', 'modules', 'units_count')

    modules = ModuleSerializer(many=True)
    units_count = serializers.SerializerMethodField('get_count')

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'sourcelanguage', 'targetlanguage', 'source')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('filename', 'lineno')

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'msgid', 'msgstr', 'comments', 'locations')

    msgid = ArrayField()
    msgstr = ArrayField()
    locations = LocationSerializer(many=True)

class LanguageSerializer(serializers.Serializer):
    "settings.LANGUAGES serializer"

    id = serializers.CharField(read_only=True)
    display = serializers.CharField(read_only=True)
