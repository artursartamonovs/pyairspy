#!/usr/bin/python3
import os
from ctypes import *
import time
import sys
import wave
import struct
import argparse

try:
    from airspy import *
except ImportError:
    print("Probably unsuported version of libairspy")
    sys.exit(1)
print("Check airspy version")

AIRSPY_MAX_DEVICES=32
devices = [airspy_device_t() for i in range(0,AIRSPY_MAX_DEVICES)]

parser = argparse.ArgumentParser()
parser.add_argument("-f","--frequency")
parser.add_argument("-s","--samplerate")
parser.add_argument("-o","--outputfile")
args = parser.parse_args()

p = airspy_lib_version_t()
libairspy.airspy_lib_version(byref(p))
print("Libairspy version %d.%d.%d"%(p.major_version, p.minor_version, p.revision))

result = libairspy.airspy_init()
if (result != airspy_error.AIRSPY_SUCCESS):
    print("Airspy init failed %s (%d)"%(libairspy.airspy_error_name(result), result))
    sys.exit(1)

count = 0
for i in range(0,AIRSPY_MAX_DEVICES):
    #ref = byref(devices[i])
    res = libairspy.airspy_open(devices[i])
    if (res != 0):
        break
    count += 1

if (count<1):
    print("No airspy devices found")
    exit(1)

res = libairspy.airspy_set_sample_type(byref(devices[0]),libairspy.airspy_sample_type.AIRSPY_SAMPLE_INT16_IQ)
if (res != airspy_error.AIRSPY_SUCCESS):
    print("Couldnt set samplerate")
    sys.exit(1)

sample_rate_count = c_uint32(0)
libairspy.airspy_get_samplerates(byref(devices[0]),byref(sample_rate_count),c_uint32(0))
print("Sample rate number %d"%(sample_rate_count.value))
if sample_rate_count.value<1:
    print("Found 0 samplerates")
    sys.exit(1)
#supported_samplerates = (c_uint32 * sample_rate_count.value)(0)
#libairspy.airspy_get_samplerates(byref(devices[0]),supported_samplerates,sample_rate_count)

#print("Supported samplerates")
#for i in range(0,count):
#    print("%d"%(supported_samplerates[i]))

""""
libairspy.airspy_set_samplerate()

libairspy.airspy_board_partid_serialno_read()

libairspy.airspy_set_rf_bias()

libairspy.airspy_start_rx()

libairspy.airspy_set_freq()

while (libairspy.airspy_is_streaming()):
    pass
"""
libairspy.airspy_exit()
