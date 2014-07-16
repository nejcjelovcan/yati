import json

from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from rest_framework import viewsets, response, permissions, renderers
from rest_framework.decorators import action

import serializers
from models import Project, Store, Unit, Module, Location, Token, User, StoreLog, UnitLog, LANGUAGES
from yati_api.settings import get_setting
from yati_api.permissions import UnitPermissions

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
    permission_classes = (UnitPermissions,)

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
    
    permission_classes = (permissions.AllowAny,)

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

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.none()
    permission_classes = (permissions.IsAdminUser,)

    def create(self, request):
        """
        This will make a new inactive user with email and language
        Invite token will also be created for new user
        If project_id is passed, contribute_project permission will be added for user
        """
        user = None
        lang = request.DATA.get('language')
        email = request.DATA.get('email')

        with transaction.atomic():
            try:
                validate_email(email)
                user = User.objects.create_user(email=email)
            except ValidationError, e:
                return response.Response(dict(email=e.messages), status=400)
            except ValueError, e:
                return response.Response(dict(email=e.args), status=400)
            except IntegrityError, e:
                return response.Response(dict(email=['User with this email already exists']), status=400)

        if lang:
            user.set_languages([lang])
            user.save()
        token = Token.objects.create_token(type='invite', user=user)
        if request.DATA.get('project_id'):
            from guardian.shortcuts import assign_perm
            try:
                project = Project.objects.get(id=request.DATA.get('project_id'))
                assign_perm('contribute_project', user, project)
            except Project.DoesNotExist:
                pass

        return response.Response(serializers.UserSerializer(user).data)

class StoreLogViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StoreLogSerializer
    queryset = StoreLog.objects.all()
    permission_classes = (permissions.IsAdminUser,)

class UnitLogViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UnitLogSerializer
    queryset = UnitLog.objects.all()
    permission_classes = (permissions.IsAdminUser,)


# Mock model and queryset for language
# this is fugly @TODO
class Language(dict):
    @property
    def id(self): return self.get('id')

    @property
    def display(self): return self.get('display')

class LanguageQueryset(list):
    def __init__(self):
        super(LanguageQueryset, self).__init__(sorted([Language(id=item, display=LANGUAGES[item]) for item in LANGUAGES], key=lambda l: l.get('id')))

    def _clone(self):
        import copy
        return copy.copy(self)

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    "@TODO obsolete? we include languages statically..."
    serializer_class = serializers.LanguageSerializer
    queryset = LanguageQueryset()
    permission_classes = (permissions.AllowAny,)    # this is bad, but we're read only
    paginate_by = 500

@ensure_csrf_cookie
def main(request):
    data = dict()
    if request.user.is_anonymous():
        post = request.method=='POST'
        form = AuthenticationForm(data=request.POST if post else None)
        if post and form.is_valid():
            login(request, form.user_cache)
            return redirect(reverse('yati-main'))
        else: data['login_form'] = form
    else:
        context = dict(request=request)
        renderer = renderers.JSONRenderer()
        data['static_data'] = renderer.render(dict(
            languages = serializers.LanguageSerializer(LanguageQueryset(), context=context, many=True).data,
            user = serializers.UserSerializer(request.user, context=context).data
            # projects = serializers.ProjectSerializer(Project.objects.all().get_for_user(request.user).distinct('id'), context=context, many=True).data
            # @TODO ^^ see App model on the front end
        ))

    return render_to_response('main.html', data, context_instance=RequestContext(request))

def logout(request):
    auth_logout(request)
    return redirect(reverse('yati-main'))

def invite(request, token):
    if not request.user.is_anonymous():
        return redirect(reverse('yati-main'))

    try:
        tok = Token.objects.get(hash=token)
    except Token.DoesNotExist, e:
        return redirect(reverse('yati-main'))

    if not tok.valid:
        return redirect(reverse('yati-main'))

    user = tok.user
    post = request.method == 'POST'
    form = SetPasswordForm(user, data=request.POST if post else None)
    data = dict(form=form, invite_user=user)

    if post and form.is_valid():
        form.save()
        tok.valid = False
        tok.save()
        user.is_active = True
        user.save()
        user = authenticate(email=user.email, password=form.cleaned_data['new_password1'])
        login(request, user)
        return redirect(reverse('yati-main'))
    return render_to_response('invite.html', data, context_instance=RequestContext(request))