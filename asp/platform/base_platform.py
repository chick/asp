__author__ = 'Chick Markley'

import sys
import re
import subprocess
from asp.util import singleton


def is_mac():
    return sys.platform == 'darwin'


def is_linux():
    return sys.platform.find('linux') != -1


@singleton
class BasePlatform(object):
    raw_info = []
    @staticmethod
    def update_info():
        BasePlatform.raw_info = BasePlatform.get_raw_info()

        parser_list = []
        if is_mac():
            parser_list = [
                CP("num_cores", ".*core_count:\s+(\d+).*", conv=int)
            ]
        elif is_linux():
            parser_list = [
                CP("num_processors", ".^processor\s*:\s+(\d+).*", acc=True, conv=int),
                CP("num_cores", ".*cpu cores\s*:\s+(\d+).*", default=0, acc=True, conv=int)
            ]
        for config_parser in parser_list:
            # print 'config parser ', config_parser.attr
            BasePlatform.__dict__[config_parser.attr] = config_parser.apply(BasePlatform.raw_info)

    @staticmethod
    def get_raw_info():
        if is_mac():
            return subprocess.check_output(['sysctl', '-a']).split('\n')
        elif is_linux():
            return open("/proc/cpuinfo", "r").readlines()


class CP(object):
    """
    configuration parser, a name a regex, used to pull out a field
    and whether to accumulate the field, if found on multiple lines
    """
    def __init__(self, attr, regex, default=None, acc=False, conv=lambda x: x):
        self.attr = attr
        self.regex = re.compile(regex)
        self.default = 0 if acc else default
        self.accumulate = acc
        self.conv = conv

    def apply(self, text_lines):
        value = self.default
        for line in text_lines:
            m = self.regex.match(line)
            if m is not None:
                if self.accumulate:
                    value += self.conv(m.group(1))
                else:
                    value = self.conv(m.group(1))
        return value


class CompilerDetector(object):
    """
    Detect if a particular compiler is available by trying to run it.
    """
    def detect(self, compiler):
        from pytools.prefork import call_capture_output, ExecError
        try:
            return_code, stdout, stderr = call_capture_output([compiler, "--version"])
        except ExecError:
            return False

        return return_code == 0




