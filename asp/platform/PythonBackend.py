__author__ = 'Chick Markley'

from asp.jit.asp_module import ASPBackend


class PythonBackend(ASPBackend):
    """
    Degenerate backend for testing.
    Create backend that runs python
    """
    def __init__(self,cache_dir=None):
        super(PythonBackend,self).__init__(
            PythonModule(),
            None,
            cache_dir=cache_dir
        )

    @staticmethod
    def is_present():
        return True


class PythonModule(object):
    pass
