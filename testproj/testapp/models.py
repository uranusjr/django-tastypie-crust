#!/usr/bin/env python
# -*- coding: utf-8

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _


class Homepage(models.Model):
    user = models.ForeignKey('auth.User')
    url = models.URLField()

    class Meta:
        verbose_name = _('Homepage')
        verbose_name_plural = _('Homepages')

    def __unicode__(self):
        format = ugettext('Homepage %(url)s of user %(username)s')
        return format % {'url': self.url, 'username': self.user.username}
