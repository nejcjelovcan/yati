from django.utils.translation import ugettext as _

from rest_framework.routers import DefaultRouter

import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'stores', views.StoreViewSet)
router.register(r'units', views.UnitViewSet)
router.register(r'languages', views.LanguageViewSet, _('Language'))
urlpatterns = router.urls