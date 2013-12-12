from django.conf.urls import patterns, include, url
from tastypie.api import Api
from testapp.resources import UserResource


v1 = Api(api_name='v1')
v1.register(UserResource())


urlpatterns = patterns(
    '',
    url(r'^api/', include(v1.urls))
)
