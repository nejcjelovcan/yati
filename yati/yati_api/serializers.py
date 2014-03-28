import json

from django import forms
from django.utils.translation import ugettext as _

from rest_framework import serializers, fields

from models import Project, Store, Unit, Location, Module

class ArrayField(fields.CharField):
    type_name = 'ArrayField'
    type_label = 'list'
    form_field_class = forms.CharField
    widget = forms.Textarea

    def from_native(self, value):
        if isinstance(value, six.string_types) or value is None:
            return value
        return json.dumps(value)


# class CharField(WritableField):
#     type_name = 'CharField'
#     type_label = 'string'
#     form_field_class = forms.CharField

#     def __init__(self, max_length=None, min_length=None, *args, **kwargs):
#         self.max_length, self.min_length = max_length, min_length
#         super(CharField, self).__init__(*args, **kwargs)
#         if min_length is not None:
#             self.validators.append(validators.MinLengthValidator(min_length))
#         if max_length is not None:
#             self.validators.append(validators.MaxLengthValidator(max_length))

#     def from_native(self, value):
#         if isinstance(value, six.string_types) or value is None:
#             return value
#         return smart_text(value)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name')

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'sourcelanguage', 'targetlanguage', 'source')

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'msgid', 'msgstr', 'comments', 'locations')

    msgid = ArrayField()
    msgstr = ArrayField()

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('id', 'name', 'pattern')

class LanguageSerializer(serializers.Serializer):
    "settings.LANGUAGES serializer"

    id = serializers.CharField(read_only=True)
    display = serializers.CharField(read_only=True)

    # def restore_fields(self, data, files):
    #     if data is not None and not isinstance(data, tuple):
    #         self._errors['non_field_errors'] = ['Invalid data']
    #         return None

    #     return {'id': data[0], 'display': data[1]}