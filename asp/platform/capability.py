__author__ = 'Chick Markley'

import sys
import subprocess
import re
import abc
import asp.platform.base_platform as base_platform


class Capability(object):
    """
    Warning: This class is deprecated.  Use the functions
    in base_platform in this package instead

    base class for implementing capabilities
    """
    def __init__(self):
        self._is_mac = base_platform.is_mac()
        self._is_linux = base_platform.is_linux()
        self.raw_info = None

    def get_compilers(self):
        pass

    def is_mac(self):
        return self._is_mac

    def is_linux(self):
        return self._is_linux

    def parse_num_cores(self):
        matcher = re.compile("processor\s+:")
        count = 0
        for line in self.raw_info:
            if re.match(matcher, line):
                count += 1
        return count

    def parse_cpu_info(self, item):
        matcher = re.compile(item + "\s+:\s*(\w+)")
        for line in self.raw_info:
            if re.match(matcher, line):
                return re.match(matcher, line).group(1)

    def validate(self):
        #TODO write this
        pass

