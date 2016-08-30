#!/bin/python3
import serial
import sys

if sys.version_info[0] != 3:
  print("This script requires python 3")
  sys.exit(1)

serial_path = '/dev/ttyUSB0'
baudrate = 9600

ser = serial.Serial(serial_path, baudrate, timeout=10)

cmd = input('$: ')
while(cmd != "exit"):
  sent_cmd = (cmd + "\r").encode('utf-8')
  print(sent_cmd)
  ser.write(sent_cmd)
  cmd = input('$: ')


