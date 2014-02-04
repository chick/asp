__author__ = 'Chick Markley'

import asp.platform.capability as capability


class OpenCl(object):
    """
    encapsulate knowledge about OpenCl
    """
    _is_available = None

    @staticmethod
    def is_available():
        if OpenCl._is_available is None:
            if capability.Capability().is_mac():
                OpenCl._is_available = True
            elif capability.Capability().is_linux():
                OpenCl._is_available = True
            pass
        return OpenCl._is_available

    @staticmethod
    def install():
        print "asp:open_cl:install is unsupported"
        raise Exception
