#!/usr/bin/python3
from ctypes import *
import sys

try:
    from airspy import *
except ImportError:
    print("Probably unsuported version of libairspy")
    sys.exit(1)

AIRSPY_MAX_DEVICES=32
devices = [POINTER(airspy_device_t)() for i in range(0,AIRSPY_MAX_DEVICES+1)]

print("Check airspy version")
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
    res = libairspy.airspy_open(byref(devices[i]))
    if (res != 0):
        break
    count += 1

print("Found %d arispy devices"%(count))

# assume first one allways there


libairspy.airspy_exit()
