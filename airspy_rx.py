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
devices = [POINTER(airspy_device_t)() for i in range(0,AIRSPY_MAX_DEVICES+1)]
#device_ = airspy_device_t()
#print(f" device so={sizeof(device_)}")
#device = byref(device_)

print(f" airspy_transfer_t ={sizeof(airspy_transfer_t)}")

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
    ref = devices[i]
    res = libairspy.airspy_open(devices[i])
    if (res != 0):
        break
    count += 1


if (count<1):
    print("No airspy devices found")
    exit(1)
device = devices[0]

#ret = libairspy.airspy_open(device)
#if ret != airspy_error.AIRSPY_SUCCESS:
#    print("Couldnt open device")
#    sys.exit(0)

res = libairspy.airspy_set_sample_type(device,airspy_sample_type.AIRSPY_SAMPLE_INT16_IQ)
if (res != airspy_error.AIRSPY_SUCCESS):
    print("Couldnt set samplerate")
    sys.exit(1)

sample_rate_count = c_uint32(0)
libairspy.airspy_get_samplerates(device,byref(sample_rate_count),c_uint32(0))
print("Sample rate number %d"%(sample_rate_count.value))
if sample_rate_count.value<1:
    print("Found 0 samplerates")
    sys.exit(1)

supported_samplerates = (c_uint32 * sample_rate_count.value)(0)
libairspy.airspy_get_samplerates(device,supported_samplerates,sample_rate_count)

print("Supported samplerates")
for i in range(0,count+1):
    print("%d"%(supported_samplerates[i]))


ret = libairspy.airspy_set_samplerate(device,supported_samplerates[0])
if ret != airspy_error.AIRSPY_SUCCESS:
    print("Couldn't set samplerate")
    sys.exit(1)

#libairspy.airspy_board_partid_serialno_read()

#libairspy.airspy_set_rf_bias()

def rx_callback(transfer):
    print("RX callback")
    print(f"Sample count {transfer.sample_count}")
    return 0

print("Here 1")
ret = libairspy.airspy_start_rx(device, airspy_sample_block_cb_fn(rx_callback), None)
if ret != airspy_error.AIRSPY_SUCCESS:
    print("Cant start RX")
    sys.exit(1)
print("Here 2")
libairspy.airspy_set_freq(device, 100000000) #100M
print("Here 3")
time.sleep(5)
print("Here 4")
count = 10
while (count>0) and (libairspy.airspy_is_streaming(device) == airspy_error.AIRSPY_TRUE):
    time.sleep(1)
    count -= 1


print("Here 4")
libairspy.airspy_close(device)

libairspy.airspy_exit()
