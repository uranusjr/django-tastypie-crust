#!/usr/bin/env python
# -*- coding: utf-8

import json
from django.test import Client, TestCase
from nose.tools import eq_, assert_greater, assert_raises
from tastypie.exceptions import NotFound


def _login(client=None):
    if client is None:
        client = Client()
    return client.post('/api/v1/user/login/', {
        'username': 'uranusjr', 'password': 'admin'
    })


class UserResourceTests(TestCase):

    fixtures = ['users.json']

    def _get_users(self, client=None):
        if client is None:
            client = Client()
        response = client.get('/api/v1/user/')
        return json.loads(response.content)

    # Test static action
    def test_action_all(self):
        client = Client()
        response = client.get('/api/v1/user/all/')
        eq_(response.status_code, 200)

        # Because /all/ contains inactive users
        assert_greater(
            len(json.loads(response.content)['objects']),
            len(self._get_users()['objects'])
        )

    # Test "allowed"
    def test_action_login(self):
        client = Client()
        response = client.get(
            '/api/v1/user/login/',
            {'username': 'uranusjr', 'password': 'admin'}
        )
        eq_(response.status_code, 405)  # Should not allow GET

        response = _login(client)
        eq_(response.status_code, 200)

    # Test plain action (default static=False)
    def test_action_full_name(self):
        client = Client()
        response = client.get('/api/v1/user/1/full_name/')
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(data['first_name'], 'Tzu-ping')
        eq_(data['last_name'], 'Chung')

    # Test non-action
    def test_non_action(self):
        client = Client()
        with assert_raises(NotFound):
            client.get('/api/v1/user/not_an_action/')
        with assert_raises(NotFound):
            client.get('/api/v1/user/1/not_an_action/')
