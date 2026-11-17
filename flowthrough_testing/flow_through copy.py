
import pandas as pd
import time
import json
from datetime import datetime
import re
import navis_com
from navis_com.com import *


#--------------Parameters---------------------#
run_until = "2025-01-01 00:00"  # YYYY-MM-DD HH:MM
# Folder of where to save pickle files
save_directory = 'G://Shared drives//WHOI Argo//BGC//Float Tracking//flow_through_data'
#---------------------------------------------#

# Get user input of com port
print("Com port:")
com = input()


nc = navis_float_com(com, save_directory)

# Dataframe
data = pd.DataFrame(columns=['DATE', 'SN', 'PRES', 'TEMP', 'PSAL', 'O2_PHASE_DELAY', 'O2_TEMPERATURE_VOLTAGE',
                    'MCOMS1', 'MCOMS2', 'MCOMS3', 'PH_VRS1', 'PH_VRS', 'PH_VK', 'PHIB', 'PHIK', 'PHVIN', 'PHVOUT'])
now = datetime.now()

nc.ser.reset_output_buffer()

while now < datetime.strptime(run_until, "%Y-%m-%d %H:%M"):

    print("     Waiting...")

    # while datetime.now().minute not in {0,5,10,15,20,25,30,35,40,45,50,55}: #Timing
    # time.sleep(1)

    try:
        now = datetime.now()

        # Wake float
        nc.wake_float()

        # Get SN
        time.sleep(1)
        nc.ser.write(b'n')

        time.sleep(1)

        mo = nc.search_buffer(r"\d+")
        print(mo)
        nc.serial_number(mo.group(0))
        # Get sample
        print("     Getting Sample...")
        nc.ser.write(b's')
        time.sleep(0.5)
        nc.ser.write(b'x')
        time.sleep(30)
        mo = nc.search_buffer(r"\[.*\]")

        line = mo.group(0)
        print(line)
        line = line.split(",")
        print(line)
        # Remove characters and convert to float
        line = [
            float(x.translate({ord(c): None for c in '[ dbCPSUusV]'})) for x in line]
        print(line)
        print("       Getting pH Sample...")
        nc.ser.write(b'x')
        time.sleep(.25)
        nc.ser.write(b's')
        time.sleep(10)
        mo = nc.search_buffer(r"-.*Out")
        line2 = mo.group(0)
        line2 = line2.split(",")
        print(line2)
        line2 = [float(x.translate(
            {ord(c): None for c in '[ VrsVkIkIbVbattInVbattOut]'})) for x in line2]
        print(line2)

        '''print('           Getting Nitrate Sample')
        nc.ser.write(b'w')
        print('sleepingss')
        time.sleep(20)
        mo = nc.search_buffer(r".*?\n.*")
        print(mo)

        time.sleep(1)
        nc.ser.write(b's')
        print('sleeping3')
        time.sleep(10)

        mo = nc.search_buffer(r":.*uM")
        print(mo)
        '''
        print("     Getting Sample...")
        '''nc.ser.write(b'w')
        print('waking suna')
        time.sleep(17)
        nc.ser.write(b'p')
        print('PTS Sampling')
        time.sleep(30)
        nc.ser.write(b's')
        #nc.ser.reset_input_buffer()
        #nc.ser.reset_output_buffer()
        print('Nitrate Sampling')
        time.sleep(5)
        to = nc.ser.readlines()
        nc.ser.write(b'q')
        time.sleep(5)
        mo = re.findall(r'Isus NO3: .*uM',str(to))
        line3 = mo
        line3 = [str(line3)]
        print(line3)
        line3 = re.findall(r'-?\d*\.\d*',str(line3))
        #line3 = [float(x.translate({ord(c): None for c in '[Isus NO3:uM]'})) for x in line3]
        print(line3)
        line3=[float(line3[0])]
        print('line 3 float')'''
        print('combining lines')
        line = line + line2 #+ line3
        print(line)
        

        # Add serial number and date
        print('adding serial number and date')
        line.insert(0, nc.sn)
        line.insert(0, now)
        print(line)

        # Add to dataframe
        line_series = pd.Series(line, index=data.columns)
        print('adding to dataframe')
        data = pd.concat([data, pd.DataFrame([line_series])],
                         ignore_index=True)
        print(data)
        # Save data - overwrites
        print('gettingcurrenttime')
        current_time = now.strftime("%Y%m%d")
        print('got time')
        data.to_pickle(save_directory+'/F'+nc.sn+"_"+current_time+'.pkl')
        print('datasaved')
        time.sleep(5)

        # Freeze float
        nc.freeze_float()
        print(data.tail())

        # Wait additional 30 seconds
        time.sleep(30)
    except:
        nc.ser.write(b'q')
        print('failed')
        time.sleep(5)


nc.ser.close()  # close serial connection
