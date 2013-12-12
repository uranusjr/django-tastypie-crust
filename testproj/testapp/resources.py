#!/usr/bin/env python
# -*- coding: utf-8

from django.contrib.auth import get_user_model
from tastypie import resources
from tastycrust.resources import ActionResourceMixin, action


class UserResource(ActionResourceMixin, resources.ModelResource):
    class Meta:
        queryset = get_user_model().objects.all()
        resource_name = 'user'

    @action
    def login(self, request, *args, **kwargs):
        return self.create_response(request, kwargs)
