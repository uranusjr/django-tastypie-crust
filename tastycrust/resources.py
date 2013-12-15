#!/usr/bin/env python
# -*- coding: utf-8

__all__ = ['ActionResourceMixin', 'action', 'is_action']


import inspect
from functools import wraps
from django.conf.urls import url
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized
from tastypie.utils import trailing_slash


def is_action(obj):
    return inspect.ismethod(obj) and getattr(obj, 'is_action', False)


def action(name=None, url=None, static=False,
           allowed=None, login_required=False):

    if callable(name):  # Used as @action without invoking
        wrapped = name
        name = None
    else:               # Used as @action(...)
        wrapped = None

    def decorator(func):

        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if allowed is not None:
                self.method_check(request, allowed)
            if login_required and not request.user.is_authenticated():
                raise ImmediateHttpResponse(
                    HttpUnauthorized('Log in required for this action')
                )
            return func(self, request, *args, **kwargs)

        wrapper.is_action = True
        wrapper.action_is_static = static
        wrapper.action_name = name
        wrapper.action_url = url

        return wrapper

    if wrapped is not None:
        return decorator(wrapped)
    return decorator


class ActionResourceMixin(object):
    def prepend_urls(self):
        urls = super(ActionResourceMixin, self).prepend_urls()
        action_methods = inspect.getmembers(type(self), predicate=is_action)
        for name, method in action_methods:
            action_name = method.action_name or name
            url_name = 'api_action_' + action_name
            action_url = method.action_url
            if action_url is not None:
                pattern = r'^{action_url}{slash}$'
                action_url = action_url.strip('/')
            elif method.action_is_static:
                pattern = r'^(?P<resource_name>{resource})/{name}{slash}$'
                url_name = 'api_action_static_' + action_name
            else:
                pattern = (r'^(?P<resource_name>{resource})/'
                           '(?P<{detail_uri}>.*?)/{name}{slash}$')
            pattern = pattern.format(
                action_url=action_url,
                resource=self._meta.resource_name,
                detail_uri=self._meta.detail_uri_name,
                name=action_name, slash=trailing_slash()
            )
            urls.insert(0, url(pattern, self.wrap_view(name), name=url_name))
        return urls
