__author__ = 'Chick Markley'

import codepy.toolchain
from asp.util import memoized
from asp.jit.asp_module import ASPBackend

class OpenmpBackend(ASPBackend):
    toolchain = None
    def __init__(self):
        self._has_open_mp = None
        OpenmpBackend.toolchain = codepy.toolchain.guess_toolchain()
        pass


    @staticmethod
    @memoized
    def is_present():
        raise Exception("Openmp not supported yet")
        import tempfile
        from pytools.prefork import call_capture_output

        f = open( tempfile.gettempdir() + "has_open_mp.cpp", "w+" )
        print >> f, """
                #include <omp.h>
                #include <stdio.h>
                int main() {
                #pragma omp parallel
                printf("Hello from thread %d, nthreads %d\n", omp_get_thread_num(), omp_get_num_threads());
                }
        """
        try:
            return_code, stdout, stderr = call_capture_output([OpenmpBackend.tool_chain, "--version"])
        except:
            return_code = 1
            return False

        return return_code == 0
