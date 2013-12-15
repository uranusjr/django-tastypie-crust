#!/usr/bin/env python
# -*- coding: utf-8

from tastypie.authentication import Authentication


class AnonymousAuthentication(Authentication):

    allowed_methods = ['GET']

    def __init__(self, allowed=None):
        if allowed is not None:
            self.allowed_methods = [s.upper() for s in allowed]

    def is_authenticated(self, request, **kwargs):
        return (request.method in self.allowed_methods)
