__author__ = 'Chick Markley'

import asp.config

detector = asp.config.PlatformDetector()

print "cudas ", detector.get_num_cuda_devices()
