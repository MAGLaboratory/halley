import serial


serial_path = '/dev/ttyUSB0'
baudrate = 9600

ser = serial.Serial(serial_path, baudrate, timeout=10)

cmd = input('$: ')
while(cmd != "exit"):
  sent_cmd = (cmd + "\r").encode('utf-8')
  print(sent_cmd)
  ser.write(sent_cmd)
  cmd = input('$: ')


