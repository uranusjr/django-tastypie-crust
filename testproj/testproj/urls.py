from django.conf.urls import patterns, include, url
from tastypie.api import Api
from testapp.resources import UserResource, HomePageResource


v1 = Api(api_name='v1')
v1.register(UserResource())
v1.register(HomePageResource())


urlpatterns = patterns(
    '',
    url(r'^api/', include(v1.urls))
)
