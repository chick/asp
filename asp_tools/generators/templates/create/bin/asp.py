#!/usr/bin/env python

__author__ = 'Chick Markley'

import sys

def asp(*args):
    """
    front end  for asp commands
    """
    print "running asp with args %s" % args

if __name__ == '__main__':
    asp(*sys.argv[1:])
