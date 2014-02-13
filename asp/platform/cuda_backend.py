from subprocess import CalledProcessError

__author__ = 'Chick Markley'

import codepy
import codepy.jit
import codepy.toolchain
import codepy.bpl
import codepy.cuda
import asp.util
from asp.jit.specialized_functions import HelperFunction
from asp.platform.ASPBackend import ASPBackend
from asp.platform.capability import CompilerDetector
import asp.codegen.cpp_ast as cpp_ast


class CudaBackend(ASPBackend):
    """
    encapsulates knowledge about using cuda
    """

    def __init__(self, boost_backend, cache_dir=None):
        super(CudaBackend, self).__init__(
            codepy.cuda.CudaModule(boost_backend.module),
            codepy.toolchain.guess_nvcc_toolchain(),
            asp.util.get_cache_dir(cache_dir),
            host_toolchain=boost_backend.toolchain
        )

        cuda_util_funcs = [("""
            void set_device(int dev) {
              int GPUCount;
              cudaGetDeviceCount(&GPUCount);
              if(GPUCount == 0) {
                dev = 0;
              } else if (dev >= GPUCount) {
                dev  = GPUCount-1;
              }
              cudaSetDevice(dev);
            }""", "set_device"),
                           ("""
            boost::python::tuple device_compute_capability(int dev) {
              int major, minor;
              cuDeviceComputeCapability(&major, &minor, dev);
              return boost::python::make_tuple(major, minor);
            }""", "device_compute_capability"),
                           ("""
            int get_device_count() {
              int count;
              cudaGetDeviceCount(&count);
              return count;
            }""", "get_device_count"),
                           ("""
            int device_get_attribute( int attr, int dev) {
              int pi;
              cuDeviceGetAttribute(&pi, (CUdevice_attribute)attr, dev);
              return pi;
            }""", "device_get_attribute"),
                           ("""
            size_t device_total_mem(int dev) {
                size_t bytes;
                cuDeviceTotalMem(&bytes, dev);
                return bytes;
            }""", "device_total_mem")]

        self.local_utility_functions = {}
        for body, name in cuda_util_funcs:
            self.local_utility_functions[name] = HelperFunction(name,body,self)
#            self.add_helper_function(body, name, backend='cuda')
        # TODO: Decide if this should default to always true?
        self.module.boost_module.add_to_preamble([cpp_ast.Include('cuda_runtime.h')])

        self.cuda_device_id = None

    def __getattr__(self, name):
        if name in self.local_utility_functions:
            return self.local_utility_functions[name]
        else:
            raise AttributeError("No method %s found; did you add it to this ASPModule?" % name)

    def get_num_cuda_devices(self):
        return self.get_device_count()

    def set_cuda_device(self, device_id):
        self.cuda_device_id = device_id
        self.set_device(device_id)

    def get_cuda_info(self):
        info = {}
        if self.cuda_device_id is None:
            raise RuntimeError("No CUDA device selected. Set device before querying.")
        attribute_list = [  # from CUdevice_attribute_enum at cuda.h:259
            ('max_threads_per_block', 1),
            ('max_block_dim_x', 2),
            ('max_block_dim_y', 3),
            ('max_block_dim_z', 4),
            ('max_grid_dim_x', 5),
            ('max_grid_dim_y', 6),
            ('max_grid_dim_z', 7),
            ('max_shared_memory_per_block', 8)]
        d = self.cuda_device_id
        for key, attr in attribute_list:
            info[key] = self.device_get_attribute(attr, d)
        info['total_mem'] = self.device_total_mem(d)
        version = self.device_compute_capability(d)
        info['capability'] = version
        info['supports_int32_atomics_in_global'] = False if version in [(1, 0)] else True
        info['supports_int32_atomics_in_shared'] = False if version in [(1, 0), (1, 1)] else True
        info['supports_int64_atomics_in_global'] = False if version in [(1, 0), (1, 1)] else True
        info['supports_warp_vote_functions'] = False if version in [(1, 0), (1, 1)] else True
        info['supports_float64_arithmetic'] = False if version in [(1, 0), (1, 1), (1, 2)] else True
        info['supports_int64_atomics_in_global'] = False if version[0] == 1 else True
        info['supports_float32_atomic_add'] = False if version[0] == 1 else True
        return info

    #
    # the following are static class methods
    #
    _has_cuda = None

    @staticmethod
    def is_present():
        if CudaBackend._has_cuda is None:
            try:
                CudaBackend._has_cuda = CompilerDetector().detect("nvcc")
            except CalledProcessError:
                CudaBackend._has_cuda = False
        return CudaBackend._has_cuda
