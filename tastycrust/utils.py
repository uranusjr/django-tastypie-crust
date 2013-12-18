#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import base64
import collections
import copy
import urlparse
import six
from io import StringIO
from django.http.multipartparser import MultiPartParserError
from django.contrib import auth
from django.utils.encoding import force_text
from tastypie.serializers import Serializer, UnsupportedFormat
from tastypie.bundle import Bundle


__all__ = ['authenticate', 'AUTH_SOURCE_BASIC', 'AUTH_SOURCE_POST', 'owned']


def _serializer_factory(formats):
    content_types = copy.copy(Serializer.content_types)
    content_types['form'] = 'application/x-www-form-urlencoded'
    content_types['form_data'] = 'multipart/form-data'

    if formats is None:
        formats = Serializer.formats + ['form', 'form_data']
    else:
        content_types = {key: value for key, value in content_types.items()
                         if key in formats}

    class _Serializer(Serializer):
        def from_form(self, data):
            return dict(urlparse.parse_qsl(data))

        def from_form_data(self, data):
            try:
                post, files = self.request.parse_file_upload(
                    self.request.META, StringIO(data)
                )
            except MultiPartParserError:
                post = {}
            return {k: post[k] for k in post}

    _Serializer.formats = formats
    _Serializer.content_types = content_types

    return _Serializer


def AUTH_SOURCE_BASIC(request, formats=None):
    try:
        auth_header = request.META['HTTP_AUTHORIZATION']
    except KeyError:
        return {}
    parts = auth_header.split(' ', 1)
    if len(parts) != 2 or parts[0] != 'Basic':
        return {}
    username, password = base64.b64decode(parts[1]).split(':', 1)
    return {'username': username, 'password': password}


def AUTH_SOURCE_POST(request, formats=None):
    serializer = _serializer_factory(formats)()
    serializer.request = request
    format = request.META.get('CONTENT_TYPE', 'application/json')

    data = request.body
    if isinstance(data, six.binary_type):
        data = force_text(data)
    try:
        credentials = serializer.deserialize(data, format)
    except UnsupportedFormat:
        credentials = {}
    if not isinstance(credentials, collections.Mapping):
        return {}
    return credentials


def authenticate(request, source=AUTH_SOURCE_POST, formats=None):
    credentials = source(request, formats)
    if not credentials:
        return None
    user = auth.authenticate(**credentials)
    return user


def owned(attribute='user'):

    bundle = None
    if isinstance(attribute, Bundle):
        bundle = attribute
        attribute = 'user'

    def _owned(bundle):
        if attribute:
            user = getattr(bundle.obj, attribute, None)
        else:
            user = bundle.obj
        return (user is not None and user == bundle.request.user)

    if bundle is None:  # Used as use_in=owned(...); invoked on resource setup
        return _owned
    else:               # Used as use_in=owned and this is invoked by Tastypie
        return _owned(bundle)
