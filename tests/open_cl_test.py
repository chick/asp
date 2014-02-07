# adapted from CodePy's nvcc example.
# requires PyCuda, CodePy, ASP, and CUDA 3.0+

from asp.jit.asp_module import ASPModule
from asp.platform.open_cl_backend import OpenClBackend

import unittest2 as unittest


class OpenClTest(unittest.TestCase):
    def test_cuda_backend(self):
        self.assertTrue(OpenClBackend.is_present())

        backend = OpenClBackend()
        self.assertTrue(backend is not None)

if __name__ == '__main__':
    unittest.main()
