import re
import serial
import time
import os
from datetime import datetime


class navis_float_com:
    def __init__(self, com, save_directory):
        self.ser = serial.Serial(port='COM'+com, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0)
        self.save_directory = save_directory

    def serial_number(self, sn):
        self.sn = sn

    # Append timestamped line to check_messages logfile
    def add_log(self, msg):
        day_str = datetime.now().strftime('%Y%m%d')
        if not os.path.isdir(self.save_directory):
            print("Save directory does not exist: ", self.save_directory)
        file = open('%s/F%s_%s.log' % (self.save_directory,self.sn, day_str),'a+') # a+ will create log file if it does not exist
        file.write('%s %s\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),msg))
        print(msg)
        file.close()

    #Wake float
    def wake_float(self):
        print("     Waking float")

        self.ser.write(b'n')
        time.sleep(2)
        self.ser.write(b'n')
        time.sleep(2)
        self.ser.write(b'n')
        time.sleep(2)
        self.ser.reset_input_buffer()

    #Get buffer and search
    def search_buffer(self, search):
        lines = self.ser.readlines()
        lines_sl = [x.decode("utf-8") for x in lines]
        lines_s = ' '.join(lines_sl)
        mo = re.search(search, lines_s)
        if not mo:
            self.add_log("Error, buffer:"+lines_s)
        return mo

    #Freeze float
    def freeze_float(self):
        print('     Freezing float...')
        self.ser.reset_input_buffer()
        self.ser.write(b'i')
        time.sleep(1)
        self.ser.write(b'f')
        time.sleep(2)
        self.ser.write(b'y\r')
        time.sleep(1)
        mo = self.search_buffer(r"The float is frozen and is not deployable")
        if mo:
            self.add_log('     Float frozen')
        self.ser.reset_input_buffer()