#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['login', 'LOGIN_SOURCE_BASIC', 'LOGIN_SOURCE_POST']


import base64
import urlparse
import six
from django.contrib import auth
from django.utils.encoding import force_text
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.serializers import Serializer


def _unauthorized():
    raise ImmediateHttpResponse(HttpUnauthorized())


class _CredentialsSerializer(Serializer):

    formats = ['json', 'form']
    content_types = {
        'json': 'application/json',
        'form': 'application/x-www-form-urlencoded'
    }

    def from_form(self, data):
        return dict(urlparse.parse_qsl(data))


def LOGIN_SOURCE_BASIC(request):
    try:
        auth_header = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        _unauthorized()
    parts = auth_header.split(' ', 1)
    if len(parts) != 2 or parts[0] != 'Basic':
        _unauthorized()
    username, password = base64.b64decode(parts[1]).split(':', 1)
    return {'username': username, 'password': password}


def LOGIN_SOURCE_POST(request):
    serializer = _CredentialsSerializer()
    format = request.META.get('CONTENT_TYPE', 'application/json')
    data = request.body
    if isinstance(data, six.binary_type):
        data = force_text(data)
    return serializer.deserialize(data, format)


def login(request, source=LOGIN_SOURCE_POST, active_only=True):
    credentials = source(request)
    user = auth.authenticate(**credentials)
    if user is None:
        _unauthorized()
    if active_only and not user.is_active:
        raise ImmediateHttpResponse(HttpForbidden)
    auth.login(request, user)
    return user
