import statistics
import pandas as pd
import numpy as np
import datetime as dt
import regex as re

def split_ftest(lastdate,SNs):
    indfloat=[]
    for j in SNs:
        outfile = 'G://Shared drives/WHOI Argo/BGC/Float Tracking/flow_through_results' + '/' + str(lastdate) + '_calcs_' + ".xlsx"
        data = pd.read_excel(outfile)
        d = data.groupby('SN')
        indfloat.append(d.get_group(j))
    return(indfloat)

def diff_analysis(SN,param):
    outfile = 'G://Shared drives/WHOI Argo/BGC/Float Tracking/flow_through_results/' + str(SN) + '_calcs_' + ".xlsx"
    data = pd.read_excel(outfile)
   
    dat = data[param]
    testdate = str(data['DATE'][0])
    datdiff = dat-(statistics.median(dat))
    ptd1 = pd.DataFrame(dat, columns = [param])
    ptd1[param] = dat
    ptd1[param + '-Median'] = datdiff
    ptd1['Float Number'] = SN + ", Test Start: "+testdate
    ptd1['SN']=SN
    ptd1['DATE'] = data['DATE']
    timediff = [0]
    i=0
    for i, timedif in enumerate(data['DATE'][:-1]):
        timediff.append(np.timedelta64(data['DATE'][i+1]-data['DATE'][i], 's'))
    td = np.array(timediff).cumsum() # time after starttime
    td = td.astype(int)
    td = td.tolist()
    mo = re.findall('\d?\d?\d?\d?\d?\d?\d', str(td))
    t = []
    for i in mo:
        t.append(i)
    convert = []
    for i in t:
        f = int(i)/3600
        #f=(dt.timedelta(seconds = int(i)))
        convert.append(f)
    ptd1['PRES'] = data['PRES']
    ptd1['Time Since Test Start (hours)'] = convert
    timediff = [0]
    i=0
    for i, timedif in enumerate(data['DATE'][:-1]):
        timediff.append(np.timedelta64(data['DATE'][i+1]-data['DATE'][i], 's'))
    td = np.array(timediff).cumsum() # time after starttime
    td = td.astype(float)
    ptd1['PRES'] = data['PRES']
    ptd1['Time Since Test Start(s)'] = td
    return ptd1
