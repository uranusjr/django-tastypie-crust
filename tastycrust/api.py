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


__all__ = ['Api', 'autodiscover']


def _is_resource_class(obj):
    return isclass(obj) and issubclass(obj, Resource)


def autodiscover():
    for app_name in settings.INSTALLED_APPS:
        app = import_module(app_name)
        try:
            old_registry = copy(api._registry)
            import_module('.'.join([app_name, 'resources']))
        except:
            api._registry = old_registry
            if module_has_submodule(app, 'resources'):
                raise


class Api(VanillaApi):
    def register(self, resource, canonical=True, module_name='resources'):
        if isinstance(resource, Resource):
            return super(Api, self).register(resource, canonical)
        elif _is_resource_class(resource):
            return super(Api, self).register(resource(), canonical)
        app_name, resource_name = resource.split('.')
        module = import_module('.'.join([app_name, module_name]))
        resource = getattr(module, resource_name)()
        return super(Api, self).register(resource, canonical)


api = Api(api_name='v1')
