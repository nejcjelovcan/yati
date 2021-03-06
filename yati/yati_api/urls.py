from django.utils.translation import ugettext as _

from rest_framework.routers import DefaultRouter

import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
#router.register(r'stores', views.StoreViewSet)
router.register(r'units', views.UnitViewSet)
router.register(r'languages', views.LanguageViewSet, _('Language'))
router.register(r'terms', views.TermViewSet, _('Term'))
router.register(r'users', views.UserViewSet)
router.register(r'storelogs', views.StoreLogViewSet)
router.register(r'unitlogs', views.UnitLogViewSet)
urlpatterns = router.urls