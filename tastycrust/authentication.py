#!/usr/bin/env python
# -*- coding: utf-8


class AnonymousAuthentication(object):
    anonymous_allowed_methods = ['GET']

    def __init__(self, allowed=None):
        if allowed is not None:
            self.anonymous_allowed_methods = allowed

    def is_authenticated(self, request, **kwargs):
        allowed_methods = [s.upper() for s in self.anonymous_allowed_methods]
        if request.method in allowed_methods:
            return True
        return False
