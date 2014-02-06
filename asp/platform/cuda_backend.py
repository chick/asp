from subprocess import CalledProcessError

__author__ = 'Chick Markley'

import codepy
import codepy.jit
import codepy.toolchain
import codepy.bpl
import codepy.cuda
import asp.util
from asp.jit.asp_module import ASPBackend
from asp.platform.capability import CompilerDetector


class CudaBackend(ASPBackend):
    """
    encapsulates knowledge about using cuda
    """

    def __init__(self, cache_dir=None):
        super(ASPBackend, self).__init__(
            codepy.bpl.BoostPythonModule(),
            codepy.toolchain.guess_nvcc_toolchain(),
            asp.util.get_cache_dir(cache_dir),
            host_toolchain=codepy.toolchain.guess_toolchain()
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

        for body, name in cuda_util_funcs:
            self.module.add_helper_function(body, name, backend='cuda')

        self.cuda_device_id = None

    def get_num_cuda_devices(self):
        return self.module.get_device_count()

    def set_cuda_device(self, device_id):
        self.cuda_device_id = device_id
        self.module.set_device(device_id)

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
            info[key] = self.module.device_get_attribute(attr, d)
        info['total_mem'] = self.module.device_total_mem(d)
        version = self.module.device_compute_capability(d)
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
