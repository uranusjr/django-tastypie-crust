#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from importlib import import_module
from inspect import isclass, getmembers
from django.conf import settings
from tastypie.api import Api as VanillaApi
from tastypie.resources import Resource


__all__ = ['Api']


def _is_resource_class(obj):
    return isclass(obj) and issubclass(obj, Resource)


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

    def autodiscover(self):
        for app_name in settings.INSTALLED_APPS:
            if app_name == 'tastypie':
                continue
            try:
                module = import_module('.'.join([app_name, 'resources']))
            except ImportError:
                continue
            for name, klass in getmembers(module, _is_resource_class):
                resource = klass()
                if not getattr(resource._meta, 'abstract', False):
                    self.register(resource)
