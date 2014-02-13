# common utilities for all asp.* to use
from __future__ import print_function
import os

def debug_print(*args):
    if 'ASP_DEBUG' in os.environ:
        for arg in args:
            print(arg, end='')
        print()


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


def get_cache_dir(name=None):
    if name:
        cache_dir = name
    else:
        import tempfile
        if os.name == 'nt':
            username = os.environ['USERNAME']
        else:
            username = os.environ['LOGNAME']

        cache_dir = tempfile.gettempdir() + "/asp_cache_" + username

    if not os.access(cache_dir, os.F_OK):
        os.mkdir(cache_dir)
    return cache_dir

import collections
import functools


class memoized(object):
    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # un-cacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

