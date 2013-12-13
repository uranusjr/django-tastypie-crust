#!/usr/bin/env python
# -*- coding: utf-8


class AnonymousAuthentication(object):
    allowed_methods = ['GET']

    def __init__(self, allowed=None):
        if allowed is not None:
            self.allowed_methods = allowed

    def is_authenticated(self, request, **kwargs):
        return (request.method in [s.upper() for s in self.allowed_methods])
