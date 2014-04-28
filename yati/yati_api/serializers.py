import json
import locale

from django import forms
from django.utils.translation import ugettext as _

from rest_framework import serializers, fields, six

from models import Project, Store, Unit, Location, Module, User, get_user_project_permissions

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
    def get_count(self, model, lang=None):
        if not lang:
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
        fields = ('id', 'name', 'modules', 'units_count', 'targetlanguages', 'users', 'project_permissions')

    #modules = ModuleSerializer(many=True)
    modules = serializers.SerializerMethodField('get_modules')
    units_count = serializers.SerializerMethodField('get_count')
    targetlanguages = serializers.SerializerMethodField('get_targetlanguages')
    users = serializers.SerializerMethodField('get_users')
    project_permissions = serializers.SerializerMethodField('get_project_permissions')

    def get_targetlanguages(self, project):
        user = self.context.get('request').user
        langs = map(lambda l: dict(id=l, units_count=self.get_count(project, l)), project.targetlanguages)
        if len(user.get_languages()):
            langs = filter(lambda l: l['id'] in user.get_languages(), langs)
        return langs

    def get_modules(self, project):
        user = self.context.get('request').user
        qs = project.modules
        if user.has_perm('contribute_project', project) or user.has_perm('change_project'):
            qs = qs.all()
        else:
            qs = qs.get_for_user(user)
        return ModuleSerializer(qs, context=self.context, many=True).data

    def get_users(self, project):
        user = self.context.get('request').user
        if user and (user.is_staff or user.has_perm('change_project')):
            from guardian.shortcuts import get_users_with_perms
            return UserSerializer(get_users_with_perms(project).filter(is_staff=False), context=dict(project=project), many=True).data
        return []

    def get_project_permissions(self, project):
        return get_user_project_permissions(self.context.get('request').user, project)

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

    def save_object(self, obj, **kwargs):
        kwargs['event'] = ('change',)
        kwargs['user'] = self.context.get('request').user
        return super(UnitWritableSerializer, self).save_object(obj, **kwargs)

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
    country = serializers.SerializerMethodField('get_country')

    def get_country(self, lang):
        "@TODO not politically correct"
        if '-' in lang.id: return lang.id.split('-')[1]
        norm = locale.normalize(lang.id).split('_')
        if len(norm) > 1:
            return norm[1].split('.')[0].lower()
        return lang.id

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_staff', 'languages', 'permissions', 'project_permissions')

    languages = serializers.SerializerMethodField('get_languages')
    permissions = serializers.SerializerMethodField('get_permissions')
    project_permissions = serializers.SerializerMethodField('get_project_permissions')

    def get_languages(self, user):
        return map(lambda l: dict(id=l), user.get_languages())

    def get_permissions(self, user):
        permissions = []
        for perm in ('add_project',):
            if user.is_admin or user.has_perm(perm):
                permissions.append(perm)
        return permissions

    def get_project_permissions(self, user):
        prj = self.context.get('project')
        if prj:
            return get_user_project_permissions(user, prj)
