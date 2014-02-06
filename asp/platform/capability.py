__author__ = 'Chick Markley'

import sys
import subprocess
import re
import abc
import codepy


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
            retcode, stdout, stderr = call_capture_output([compiler, "--version"])
        except ExecError:
            return False

        return retcode == 0


class Capability(object):
    """
    base class for implementing capabilities
    """
    def __init__(self, mock_info=None):
        self._is_mac = sys.platform == 'darwin'
        self._is_linux = sys.platform.find('linux') != -1
        self.mock_info = mock_info
        self.raw_info = None
        self.tool_chain =  codepy.toolchain.guess_toolchain()

    @staticmethod
    @abc.abstractmethod
    def is_present():
        """override this to indicate whether sub-classed capability is present"""
        return

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

    def update_info(self):
        self.raw_info = self.get_raw_info()

        parser_list = []
        if self.is_mac():
            parser_list = [
                CP("num_cores", ".*core_count:\s+(\d+).*", conv=int)
            ]
        elif self.is_linux():
            parser_list = [
                CP("num_processors", ".^processor\s*:\s+(\d+).*", acc=True, conv=int),
                CP("num_cores", ".*cpu cores\s*:\s+(\d+).*", default=0, acc=True, conv=int)
            ]
        for config_parser in parser_list:
            # print 'config parser ', config_parser.attr
            self.__dict__[config_parser.attr] = config_parser.apply(self.raw_info)

    def get_raw_info(self):
        if self.is_mac():
            return subprocess.check_output(['sysctl', '-a']).split('\n')
        elif self.is_linux():
            return open("/proc/cpuinfo", "r").readlines()

    def validate(self):
        #TODO write this
        pass

