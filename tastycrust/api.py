#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from copy import copy
from importlib import import_module
from inspect import isclass
from django.conf import settings
from django.utils.module_loading import module_has_submodule
from tastypie.api import Api as VanillaApi
from tastypie.resources import Resource


__all__ = ['Api', 'autodiscover', 'v1']


def autodiscover():
    for app_name in settings.INSTALLED_APPS:
        app = import_module(app_name)
        try:
            old_registry = copy(v1._registry)
            import_module('.'.join([app_name, 'resources']))
        except:
            v1._registry = old_registry
            if module_has_submodule(app, 'resources'):
                raise


class Api(VanillaApi):
    def register(self, resource, canonical=True, module_name='resources'):
        if isinstance(resource, Resource):
            return super(Api, self).register(resource, canonical)
        elif isclass(resource) and issubclass(resource, Resource):
            return super(Api, self).register(resource(), canonical)
        app_name, resource_name = resource.split('.')
        module = import_module('.'.join([app_name, module_name]))
        resource = getattr(module, resource_name)()
        return super(Api, self).register(resource, canonical)


v1 = Api(api_name='v1')
