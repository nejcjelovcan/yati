from rest_framework import permissions

from yati_api.models import Project, Module

class UnitPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user.is_staff: return True

        if request.method == 'GET':
            module_id = request.GET.get('module_id')
            language = request.GET.get('language')

            if not module_id or not language: return False
            if len(user.get_languages()) and language not in user.get_languages():
                return False

            mod = Module.objects.get(id=module_id)
            if user.has_perm('contribute_module', mod)\
                or user.has_perm('change_project', mod.project)\
                or user.has_perm('contribute_project', mod.project):
                return True
            return False

        return True # @TODO this is very stupid (but object permissions arent event checked without this)

    def has_object_permission(self, request, view, unit):
        user = request.user
        if self.has_permission(request, view): return True

        print 'HAS OBJECT PERMISSION', unit

        if request.method == 'PUT':
            store = unit.store
            
            if len(user.get_languages()) and store.targetlanguage not in user.get_languages():
                return False

            if user.has_perm('contribute_project', store.project)\
                or user.has_perm('change_project', store.project):
                return True

            modules = Module.objects.get_for_unit(unit)
            for module in modules:
                if user.has_perm('contribute_module', module):
                    return True
            return False

        return False
