#!/usr/bin/env python
# -*- coding: utf-8

import base64
import json
import urllib
from django.contrib.auth.models import User
from django.test import Client, TestCase
from nose.tools import eq_, assert_greater, assert_raises
from tastypie.exceptions import NotFound


def _login(client):
    client.login(username='uranusjr', password='admin')


class UserResourceActionTests(TestCase):

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

        response = client.post('/api/v1/user/login/', {
            'username': 'uranusjr', 'password': 'admin'
        })
        eq_(response.status_code, 200)

    # Test login_required
    def test_action_logout(self):
        client = Client()
        response = client.post('/api/v1/user/logout/')
        eq_(response.status_code, 401)  # Unauthorized
        _login(client)
        response = client.post('/api/v1/user/logout/')
        eq_(response.status_code, 200)

    # Test plain action (default static=False)
    def test_action_full_name(self):
        client = Client()
        response = client.get('/api/v1/user/1/full_name/')
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(data['first_name'], 'Tzu-ping')
        eq_(data['last_name'], 'Chung')

    # Test custom action name
    def test_action_profile(self):
        client = Client()
        _login(client)

        with assert_raises(NotFound):
            client.get('/api/v1/user/1/userprofile/')

        response = client.get('/api/v1/user/1/profile/')
        eq_(response.status_code, 200)
        eq_(json.loads(response.content), {
            'first_name': 'Tzu-ping',
            'last_name': 'Chung',
            'id': 1,
            'username': 'uranusjr'
        })

        response = client.get('/api/v1/user/2/profile/')
        eq_(response.status_code, 200)
        eq_(json.loads(response.content), {'id': 2, 'username': 'normal_user'})

    # Test custom action URL
    def test_action_email(self):
        client = Client()
        _login(client)

        with assert_raises(NotFound):
            client.get('/api/v1/user/my_email/')

        response = client.get('/api/v1/user/email/')
        eq_(response.status_code, 200)
        eq_(json.loads(response.content), {'email': 'uranusjr@gmail.com'})

    # Test non-action
    def test_non_action(self):
        client = Client()
        with assert_raises(NotFound):
            client.get('/api/v1/user/not_an_action/')
        with assert_raises(NotFound):
            client.get('/api/v1/user/1/not_an_action/')


class UserResourceTests(TestCase):

    fixtures = ['users.json']

    def test_authentication(self):
        client = Client()
        response = client.get('/api/v1/user/')
        eq_(response.status_code, 200)  # Should allow anonymous read
        old_count = len(json.loads(response.content)['objects'])

        response = client.post(
            '/api/v1/user/',
            json.dumps({'username': 'new_user'}),
            content_type='application/json'
        )
        eq_(response.status_code, 401)  # Should not allow anonymous write

        _login(client)

        response = client.post(
            '/api/v1/user/',
            json.dumps({'username': 'new_user'}),
            content_type='application/json'
        )
        eq_(response.status_code, 201)  # Should allow authenticated write

        # Check that the POST is successful
        current_count = User.objects.filter(is_active=True).count()
        eq_(old_count + 1, current_count)

    def test_login_post(self):
        client = Client()
        credentials = {'username': 'uranusjr', 'password': 'admin'}

        response = client.post(
            '/api/v1/user/login_post/',
            json.dumps(credentials), content_type='application/json'
        )
        eq_(response.status_code, 200)

        response = client.post(
            '/api/v1/user/login_post/',
            urllib.urlencode(credentials),
            content_type='application/x-www-form-urlencoded'
        )
        eq_(response.status_code, 200)

        # Incorrect credentials
        credentials['password'] = 'hehe'
        response = client.post(
            '/api/v1/user/login_post/',
            urllib.urlencode(credentials),
            content_type='application/x-www-form-urlencoded'
        )
        eq_(response.status_code, 401)

    def test_login_basic(self):
        client = Client()

        # No auth header
        response = client.post('/api/v1/user/login_basic/')
        eq_(response.status_code, 401)

        credentials = base64.encodestring('%s:%s' % ('uranusjr', 'admin'))
        response = client.post(
            '/api/v1/user/login_basic/',
            HTTP_AUTHORIZATION=('Basic %s' % credentials)
        )
        eq_(response.status_code, 200)

        # Incorrect auth header format
        response = client.post(
            '/api/v1/user/login_basic/',
            HTTP_AUTHORIZATION=('%s' % credentials)
        )
        eq_(response.status_code, 401)

        # Incorrect credentials
        credentials = base64.encodestring('%s:%s' % ('uranusjr', 'hehe'))
        response = client.post(
            '/api/v1/user/login_basic/',
            HTTP_AUTHORIZATION=('Basic %s' % credentials)
        )
        eq_(response.status_code, 401)
