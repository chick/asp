__author__ = 'Chick Markley'

import sys, os
import platform

class CompilerDetector(object):
    """
    Detect if a particular compiler is available by trying to run it.
    """
    def detect(self, compiler):
        from pytools.prefork import call_capture_output
        try:
            retcode, stdout, stderr = call_capture_output([compiler, "--version"])
        except:
            return False

        return (retcode == 0)

class Capability(object):
    def __init__(self):
        self._is_mac = sys.platform == 'darwin'
        self.is_linux = 'linux' in sys.platform

    def get_compilers(self):




    def is_mac(self):
        self.is_mac
