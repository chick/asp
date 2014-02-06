# common utilities for all asp.* to use
from __future__ import print_function
import os

def debug_print(*args):
    if 'ASP_DEBUG' in os.environ:
        for arg in args:
            print(arg, end='')
        print()


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
        import tempfile, os
        if os.name == 'nt':
            username = os.environ['USERNAME']
        else:
            username = os.environ['LOGNAME']

        cache_dir = tempfile.gettempdir() + "/asp_cache_" + username

    if not os.access(cache_dir, os.F_OK):
        os.mkdir(cache_dir)
    return cache_dir



