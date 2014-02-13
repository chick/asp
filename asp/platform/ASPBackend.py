import codepy
import asp.codegen.cpp_ast as cpp_ast
import abc
import asp.jit.scala_module as scala_module

class ASPBackend(object):
    """
    Class to encapsulate a backend for Asp.  A backend is the combination of a CodePy module
    (which contains the actual functions) and a CodePy compiler toolchain.
    """
    def __init__(self, module, toolchain, cache_dir, host_toolchain=None):
        self.module = module
        self.toolchain = toolchain
        self.host_toolchain = host_toolchain
        self.compiled_module = None
        self.cache_dir = cache_dir
        self.dirty = True
        self.compilable = True

    def compile(self):
        """
        Trigger a compile of this backend.  Note that CUDA needs to know about the C++
        backend as well.
        """
        if not self.compilable: return
        if isinstance(self.module, codepy.cuda.CudaModule):
            self.compiled_module = self.module.compile(self.host_toolchain,
                                                                        self.toolchain,
                                                                        debug=True, cache_dir=self.cache_dir)
        else:
            self.compiled_module = self.module.compile(self.toolchain,
                                                       debug=True, cache_dir=self.cache_dir)
        self.dirty = False

    def get_compiled_function(self, name):
        """
        Return a callable for a raw compiled function (that is, this must be a variant name rather than
        a function name).
        """
        try:
            func = getattr(self.compiled_module, name)
        except:
            raise AttributeError("Function %s not found in compiled module." % (name,))

        return func

    @staticmethod
    @abc.abstractmethod
    def is_present():
        """override this to indicate whether sub-classed capability is present"""
        return
