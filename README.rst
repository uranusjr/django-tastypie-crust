.. image:: https://travis-ci.org/uranusjr/django-tastypie-crust.png?branch=master
   :target: https://travis-ci.org/uranusjr/django-tastypie-crust

==============
Tastypie Crust
==============

Your Tastypie just become even tastier.


+++++++++
Rationale
+++++++++

This package is really just a collection of snippets I use constantly with
Tastypie across multiple projects. They are reused so much it just makes more
sense to collect them together than copy-pasting codes everywhere.

None of the snippets in this package originate from myself. The idea of
"resource actions", in particular, came from `tastypie-actions`_ by Justin
Alexander (*aka* thelonecabbage_ on GitHub), although I re-implemented the
details quite a bit. Some other utilities are mostly collected from snippets
floating around the Internet (StackOverflow_, `djangosnippets.org`_, etc.).

.. _`tastypie-actions`: https://github.com/thelonecabbage/django-tastypie-actions
.. _thelonecabbage: https://github.com/thelonecabbage
.. _StackOverflow: http://stackoverflow.com/
.. _`djangosnippets.org`: https://djangosnippets.org


++++++++++
Components
++++++++++

---------
Resources
---------

::

    class ActionResourceMixin

Resources subclassing this mixin can have methods decorated with ``action``,
making those methods accessible throught Tastypie API.

::

    action(name=None, url=None, static=False,
           allowed=None, login_required=False, throttled=False)

Decorator that makes extra resource methods accessible through Tastypie API.


--------------
Authentication
--------------

::

    class AnonymousAuthentication

Authentication policy that only allows certain request methods go through
anonymously.


+++++++
Example
+++++++

Some example usages can be found inside ``testproj/testapp/resources.py``.


+++++++
License
+++++++

BSD 3-cluse license. See file ``LICENSE`` for its content.


++++++++++++
Contributing
++++++++++++

To run tests in this project, you need ``django-nose`` and ``coverage`` along
with obvious dependencies. Run ``python testproj/manage.py test`` in the
project root to invoke tests.
