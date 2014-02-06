__author__ = 'Chick Markley'

import os
import yaml

class AspConfiguration(object):
    """
    This class encapsulates the configuration options for a particular specializer name

    These options come from a two tiered system of configuration files.
    1 ) Look in the root directory of this specializer for asp_config.yml
    2 ) Look in the user directory for asp_config.yml
    Any options found in 2 will overwrite those found in 1)

    Usage in specializer

    Interface for reading a per-user configuration file in YAML format.  The
    config file lives in ~/.asp_config.yml (on windows, ~ is equivalent to
    \Users\<current user>).

    On initialization, specify the specializer whose settings are going to be read.

    The format of the file should contain a specializer's
    settings in its own hash.  E.g.:
    specializer_foo:
      setting_one: value
      setting_two: value
    specializer_bar:
      setting_etc: value

    """
    def __init__(self, specializer):
        try:
            self.stream = open(os.path.expanduser("~")+'/.asp_config.yml')
            self.configs = yaml.load(self.stream)
        except:
            print "No configuration file ~/.asp_config.yml found."
            self.configs = {}

        self.specializer = specializer

        #translates from YAML file to Python dictionary


    # add functionality to iterate keys?
    def get_option(self, key):
        """
        Given a key, return the value for that key, or None.
        """
        try:
            return self.configs[self.specializer][key]
        except KeyError:
            print "Configuration key %s not found" % key
            return None
