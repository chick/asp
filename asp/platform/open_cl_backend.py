__author__ = 'Chick Markley'

import codepy
import codepy.jit
import codepy.toolchain
import codepy.bpl
import asp.platform.capability as capability
import asp.util
from asp.jit.asp_module import ASPBackend


class OpenClBackend(ASPBackend):
    """
    encapsulate knowledge about OpenCl
    """
    def __init__(self,cache_dir=None):
        super(OpenClBackend, self).__init__(
            codepy.bpl.BoostPythonModule(),
            codepy.toolchain.guess_toolchain(),
            asp.util.get_cache_dir(cache_dir),
        )

    _is_available = None

    @staticmethod
    def is_present():
        if OpenClBackend._is_available is None:
            if capability.Capability().is_mac():
                OpenClBackend._is_available = True
            elif capability.Capability().is_linux():
                OpenClBackend._is_available = True
            pass
        return OpenClBackend._is_available

    @staticmethod
    def install():
        print "asp:open_cl:install is unsupported"
        raise Exception
