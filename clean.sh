#!/bin/bash

#
# get rid of stuff created by setup.py
#

echo -n Removing temporary files...
rm -fr test_install asp.egg-info build dist distribute-*.egg distribute-*.tar.gz
find -name *.pyc | xargs rm -f
echo done.
