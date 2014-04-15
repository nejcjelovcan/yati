import json

from django import forms
from django.utils.translation import ugettext as _

from rest_framework import serializers, fields, six

from models import Project, Store, Unit, Location, Module, User

class ArrayField(fields.CharField):
    """
    Array field for Unit.msgid and Unit.msgstr
    
    @TODO this is read-only and defaults to "" instead of []
    @TODO wtf
    """
    type_name = 'ArrayField'
    type_label = 'list'
    form_field_class = forms.CharField
    widget = forms.Textarea

    def from_native(self, value):
        if isinstance(value, six.string_types):
            return json.loads(value)
        elif not type(value) in (list, tuple):
            return [value]
        return value

class UnitSetCounts(object):
    def get_count(self, model):
        lang = self.context.get('request').GET.get('language')
        units = model.units
        if lang:
            units = units.by_language(target=lang)
        return [units.count(), units.done().count()]

class ModuleSerializer(serializers.ModelSerializer, UnitSetCounts):
    class Meta:
        model = Module
        fields = ('id', 'name', 'pattern', 'units_count')

    units_count = serializers.SerializerMethodField('get_count')


class ProjectSerializer(serializers.ModelSerializer, UnitSetCounts):
    class Meta:
        model = Project
        fields = ('id', 'name', 'modules', 'units_count', 'targetlanguages')

    #modules = ModuleSerializer(many=True)
    modules = serializers.SerializerMethodField('get_modules')
    units_count = serializers.SerializerMethodField('get_count')
    targetlanguages = serializers.SerializerMethodField('get_targetlanguages')

    def get_targetlanguages(self, project):
        return project.targetlanguages

    def get_modules(self, project):
        return ModuleSerializer(project.modules.get_for_user(self.context.get('request').user), context=self.context, many=True).data

# class StoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Store
#         fields = ('id', 'sourcelanguage', 'targetlanguage', 'source')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('filename', 'lineno')

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'msgid', 'msgstr', 'msgid_plural', 'msgstr_plural', 'comments')

    msgid = serializers.SerializerMethodField('get_msgid')
    msgstr = serializers.SerializerMethodField('get_msgstr')

    msgid_plural = serializers.SerializerMethodField('get_msgid_plural')
    msgstr_plural = serializers.SerializerMethodField('get_msgstr_plural')

    def get_msgid(self, unit):
        return unit.msgid[0]

    def get_msgstr(self, unit):
        return unit.msgstr[0]

    def get_msgid_plural(self, unit):
        if len(unit.msgid) > 1: return unit.msgid[1:]

    def get_msgstr_plural(self, unit):
        if len(unit.msgstr) > 1: return unit.msgstr[1:]

class UnitWritableSerializer(UnitSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'msgstr')

    msgstr = ArrayField()

class UnitTermSerializer(UnitSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'msgid', 'msgstr')

    def get_msgstr(self, unit):
        return unit.msgstr

class LanguageSerializer(serializers.Serializer):
    "settings.LANGUAGES serializer"

    id = serializers.CharField(read_only=True)
    display = serializers.CharField(read_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_admin', 'languages', 'permissions')

    languages = serializers.SerializerMethodField('get_languages')
    permissions = serializers.SerializerMethodField('get_permissions')

    def get_languages(self, user):
        return user.get_languages()

    def get_permissions(self, user):
        permissions = []
        for perm in ('add_project',):
            if user.is_admin or user.has_perm(perm):
                permissions.append(perm)
        return permissions
