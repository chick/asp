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



