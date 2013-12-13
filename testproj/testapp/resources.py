#!/usr/bin/env python
# -*- coding: utf-8

import copy
from django.contrib.auth import get_user_model, authenticate, login, logout
from tastypie import resources
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpNotFound
from tastycrust.resources import ActionResourceMixin, action


User = get_user_model()


class UserResource(ActionResourceMixin, resources.ModelResource):
    class Meta:
        queryset = User.objects.filter(is_active=True)
        resource_name = 'user'
        fields = ['id', 'username']

    def not_an_action(self, request, *args, **kwargs):
        return self.create_response(request, {})

    @action(static=True)
    def all(self, request, *args, **kwargs):
        paginator = self._meta.paginator_class(
            request.GET, User.objects.all(),
            resource_uri=self.get_resource_uri(),
            limit=self._meta.limit,
            max_limit=self._meta.max_limit,
            collection_name=self._meta.collection_name
        )
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            bundles.append(self.full_dehydrate(bundle, for_list=True))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(
            request, to_be_serialized
        )
        return self.create_response(request, to_be_serialized)

    @action(allowed=('post',), static=True)
    def login(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is None:
            raise ImmediateHttpResponse(HttpForbidden)
        if not user.is_active:
            raise ImmediateHttpResponse(HttpUnauthorized)

        login(request, user)

        bundle = self.build_bundle(obj=user, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)
        return self.create_response(request, bundle)

    @action
    def full_name(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        data = {'first_name': user.first_name, 'last_name': user.last_name}
        return self.create_response(request, data)

    @action(allowed=('post',), static=True, login_required=True)
    def logout(self, request, *args, **kwargs):
        logout(request)
        return self.create_response(request, {})

    @action(login_required=True, name='profile')
    def userprofile(self, request, *args, **kwargs):
        fields = copy.copy(self._meta.fields)
        try:
            target_user = User.objects.get(pk=kwargs['pk'])
        except User.DoesNotExist:
            raise ImmediateHttpResponse(HttpNotFound)
        else:
            if target_user == request.user:
                fields += ['first_name', 'last_name']
            data = {k: getattr(target_user, k) for k in fields}
            return self.create_response(request, data)

    @action(static=True, login_required=True, url='/user/email/')
    def my_email(self, request, *args, **kwargs):
        return self.create_response(request, {'email': request.user.email})
