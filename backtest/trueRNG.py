# !!
# !! need to "pip install pyserial"
# !!
import serial
import serial.tools.list_ports as port_list
import struct
import sys
import pandas as pd
import numpy as np

# !!
# !! don't call this directly, will lock the port
# !!
def scan_for_trueRNG_device():
	for port in port_list.comports():
		# --
		# -- following IDs are from http://www.linux-usb.org/usb.ids
		# --
		print(f"trying {port} ...")
		if(port.vid==0x04D8 and port.pid==0xF5FE):
			print(f"using {port} ...")
			return serial.Serial(port.name)
	raise "No TrueRNG device found"

def make_rnd_fn(dev0=None,buffer_size=1000):
	return make_rnd_fn_v2(dev0=dev0,buffer_size=buffer_size)

def make_rnd_fn_v1(dev0=None,buffer_size=50000):
	if(dev0==None):
		dev0 = scan_for_trueRNG_device()
	pack_len = 8
	maxint = sys.maxsize*2-1
	b0 = None
	nextloc = 0
	def rnd_fn():
		nonlocal b0,nextloc
		if(b0 is None or (pack_len+nextloc)>len(b0)):
			dev0 = scan_for_trueRNG_device()
			if(not dev0.is_open):
				dev0.open()
			b0 = bytearray( dev0.read(pack_len*buffer_size) )
			dev0.close()
			nextloc = 0
		next_val = struct.unpack(">Q",b0[nextloc+0:nextloc+pack_len])[0]/maxint
		nextloc += pack_len
		return next_val
	return rnd_fn

# --
# !! rotate the buffer instead of refetching from the generator
# !! work relative well, but not perfect. A lot faster than v1
# --
def make_rnd_fn_v2(dev0=None,buffer_size=50000):
	if(dev0==None):
		dev0 = scan_for_trueRNG_device()
	# --
	# -- anything not multiple of pack_len, and
	# -- buffer_size not dividible by it
	# -- preferably some prime number (13, 17, 19, 23, etc)
	# --
	shift_dist = 13
	pack_len = 8
	maxint = sys.maxsize*2-1
	b0 = None
	nextloc = 0
	def rnd_fn():
		nonlocal b0,nextloc
		if(b0 is None):
			dev0 = scan_for_trueRNG_device()
			if(not dev0.is_open):
				dev0.open()
			b0 = bytearray( dev0.read(pack_len*buffer_size) )
			dev0.close()
			nextloc = 0
		elif((pack_len+nextloc)>len(b0)):
			b0 = b0[shift_dist:] + b0[0:shift_dist]
			nextloc = 0
		next_val = struct.unpack(">Q",b0[nextloc+0:nextloc+pack_len])[0]/maxint
		nextloc += pack_len
		return next_val
	return rnd_fn

