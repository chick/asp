__author__ = 'Chick Markley'

import unittest2 as unittest
import asp.platform.capability as capability
from fudge import patched_context
import sys

class CpText(unittest.TestCase):
    def test_apply(self):
        # apply can convert type using conv
        cp = capability.CP('num_cores',".*core_count:\s+(\d+)",conv=int)
        num_cores = cp.apply(['machdep.cpu.core_count: 4'])
        assert num_cores == 4

        # default on no match is none
        cp = capability.CP('num_cores',".*core_count:\s+(\d+)",conv=int)
        num_cores = cp.apply(['machdep.cpu.processor: 4'])
        assert num_cores is None

        # default can be overridden
        cp = capability.CP('num_cores',".*core_count:\s+(\d+)",default=7,conv=int)
        num_cores = cp.apply(['machdep.cpu.processor: 4'])
        assert num_cores == 7

        # without conversion default is string
        cp = capability.CP('numCores',".*core_count:\s+(\d+)")
        num_cores = cp.apply(['machdep.cpu.core_count: 4'])
        assert num_cores == '4'
        assert num_cores != 4

        # cp can accumulate
        cp = capability.CP('num_cores',".*core_count:\s+(\d+)",acc=True,conv=int)
        num_cores = cp.apply(['machdep.cpu.core_count: 4','machdep.cpu.core_count: 7'])
        assert num_cores == 11


class MacTest(unittest.TestCase):
    mac_raw_info = open("mac_raw_info.txt","r").readlines()
    linux_raw_info = open("linux_raw_info.txt","r").readlines()

    def test_is_mac(self):
        with patched_context(sys, 'platform', "darwin" ):
            c = capability.Capability()
            assert c.is_mac() == True
            assert c.is_linux() == False

    def test_is_linux(self):
        with patched_context(sys, 'platform', "linux2" ):
            c = capability.Capability()
            assert c.is_mac() == False
            assert c.is_linux() == True

    def test_num_cores(self):
        c = capability.Capability()
        with patched_context( c, 'get_raw_info', lambda x: MacTest.mac_raw_info ):
            assert sum( 'machdep.cpu' in x for x in c.get_raw_info() ) > 0
            c.update_info()

            assert c.raw_info == c.get_raw_info()

            print 'num_cores ', c.num_cores
            assert c.num_cores == 4


