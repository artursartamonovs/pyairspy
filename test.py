#!/usr/bin/python3
import os
from ctypes import *
import time
import sys
import wave
import struct
try:
    from airspy import *
except ImportError:
    print("Probably unsuported version of libairspy")
    sys.exit(1)
print("Check airspy version")

device = airspy_device_t_p(None)

p = airspy_lib_version_t()
libairspy.airspy_lib_version(byref(p))
print(p.major_version)
print(p.minor_version)
print(p.revision)

result = libairspy.airspy_init()
if (result != airspy_error.AIRSPY_SUCCESS):
    print("Airspy init failed %s (%d)"%(libairspy.airspy_error_name(result), result))
    sys.exit(1)

result = libairspy.airspy_open(byref(device))

board_id = c_uint8(airspy_board_id.AIRSPY_BOARD_ID_INVALID)
#result = libairspy.airspy_board_id_read(device, byref(board_id))
print("Board ID Number: %s "%(str(board_id)))


libairspy.airspy_exit()
