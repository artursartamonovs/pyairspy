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

AIRSPY_MAX_DEVICES=32

#device = airspy_device_t_p(None)
devices = [airspy_device_t() for i in range(0,AIRSPY_MAX_DEVICES)]

print("airspy_device_t size=%d"%(sizeof(airspy_device_t)))
#print("devices %d"%(sizeof(devices)))

p = airspy_lib_version_t()
libairspy.airspy_lib_version(byref(p))
print("Libairspy version %d.%d.%d"%(p.major_version, p.minor_version, p.revision))

result = libairspy.airspy_init()
if (result != airspy_error.AIRSPY_SUCCESS):
    print("Airspy init failed %s (%d)"%(libairspy.airspy_error_name(result), result))
    sys.exit(1)

"""
result = libairspy.airspy_open(byref(device))

print("Get list of devices if there is any")
board_id = c_uint8(airspy_board_id.AIRSPY_BOARD_ID_INVALID)
result = libairspy.airspy_board_id_read(device, byref(board_id))
print("Found X devices")
print("Board ID Number: %s "%(str(board_id)))
"""
count = 0
for i in range(0,AIRSPY_MAX_DEVICES):
    #ref = byref(devices[i])
    res = libairspy.airspy_open(devices[i])
    if (res != 0):
        break
    count += 1

print("Found %d arispy devices"%(count))

# assume first one allways there


libairspy.airspy_exit()
