from django.conf.urls import url
from django.contrib import admin
from rest_framework import routers

from core import views


class OptionalTrailingSlashRouter(routers.DefaultRouter):
    """
    Make trailing slash optional in url routes
    https://github.com/encode/django-rest-framework/issues/905#issuecomment-383492553-permalink
    """
    def __init__(self, *args, **kwargs):
        super(OptionalTrailingSlashRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'


router = OptionalTrailingSlashRouter()
router.register(r'records', views.RecordViewSet, base_name='Records')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

urlpatterns += router.urls
