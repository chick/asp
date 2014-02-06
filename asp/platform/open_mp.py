__author__ = 'Chick Markley'

import subprocess
from asp.platform.capability import Capability

class OpenMp(Capability):
    def __init__(self):
        self._has_open_mp = None
        pass

    @staticmethod
    def is_present(self):
        if self._has_open_mp == None:
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
            retcode, stdout, stderr = call_capture_output([OpenMp.tool_chain, "--version"])


            self.cache_dir = tempfile.gettempdir() + "/asp_cache_" + username
        try:
            retcode, stdout, stderr = call_capture_output([compiler, "--version"])
        except:
            return False

        return (retcode == 0)
