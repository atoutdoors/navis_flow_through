import serial
from SOLO_FUNS import getsn
# SETUP COM PORT
comport=3
com = 'COM'+ str(comport)
ser = serial.Serial(com,baudrate=9600,timeout=None)

SN=getsn(ser)
print(SN)