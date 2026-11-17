
import pandas as pd
import time
import json
from datetime import datetime
import re
import navis_com
from navis_com.com import *


#--------------Parameters---------------------#
run_until = "2026-01-01 00:00"  # YYYY-MM-DD HH:MM
# Folder of where to save pickle files
save_directory = 'G://Shared drives//WHOI Argo//BGC//Float Tracking//flow_through_data'
#---------------------------------------------#

# Get user input of com port
print("Com port:")
com = input()


nc = navis_float_com(com, save_directory)

# Dataframe
data = pd.DataFrame(columns=['DATE', 'SN', 'DOXY', 'TEMP', 'O2_PHASE_DELAY', 'O2_TEMPERATURE_VOLTAGE'])
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
        time.sleep(.5)
        nc.ser.write(b'n')

        time.sleep(.5)

        mo = nc.search_buffer(r"\d+")
        print(mo)
        nc.serial_number(mo.group(0))
        # Get sample
        print("     Getting Sample...")
        nc.ser.write(b'o')
        time.sleep(0.5)
        nc.ser.write(b's')
        time.sleep(11)
        mo = nc.search_buffer(r".*")
        print(mo)
        print('step1')
        line = mo.group(0)
        print(line)
        print('step2')
        line = line.split(",")
        print(line)
        # Remove characters and convert to float
        print('step3')
        line = [
            (x.translate({ord(c): None for c in 'osOptOxSenOTPhaseRawTemp:ml/lCusecV'})) for x in line]
        print(line)
        # Add serial number and date
        line = line[3].split(" ")
        del line[2]
        print('adding serial number and date')
        line.insert(0, nc.sn)
        print('1')
        line.insert(0, now)
        print('2')
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
        data.to_excel(save_directory+'/F'+nc.sn+"_SBE83_"+current_time+'.xlsx')
        print('datasaved')
        time.sleep(.5)

        # Freeze float
        #nc.freeze_float()
        print(data.tail())

        # Wait additional 30 seconds
        #time.sleep(30)
    except:
        nc.ser.write(b'q')
        print('failed')
        time.sleep(5)


nc.ser.close()  # close serial connection
