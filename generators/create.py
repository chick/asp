__author__ = 'chick'

import sys
import os

import builder as Builder

project_directories = ["cache","code","doc","examples","templates","tests"]

if __name__ == '__main__':
    args = sys.argv

    specializer_name = args[1]

    print "create project specializer %s" % specializer_name

    builder = Builder.Builder( "create", specializer_name, verbose=True )

    builder.build(None,None)


