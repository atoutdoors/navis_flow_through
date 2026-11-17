import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np

# Input the date 
date = "05-Dec-2024"

# Read Table
data = pd.read_excel(f"G:/Shared drives/WHOI Argo/BGC/Float Tracking/flow_through_data/{date}.xlsx")

# Make Table into arrays
time = pd.to_datetime(data["time"].to_numpy())
salinity = data["s"].to_numpy()
floatnum = data["fid"].to_numpy()
pressure = data["p"].to_numpy()
temp = data["t"].to_numpy()
doxyphase = data["doxyphasedelay"].to_numpy()
doxytempv = data["doxytempvolts"].to_numpy()
vrs = data["phvrs"].to_numpy()
vk = data["phvk"].to_numpy()
eco1 = data["eco1"].to_numpy()
eco2 = data["eco2"].to_numpy()
eco3 = data["eco3"].to_numpy()
ocr1 = data["ocr1"].to_numpy()
ocr2 = data["ocr2"].to_numpy()
ocr3 = data["ocr3"].to_numpy()
ocr4 = data["ocr4"].to_numpy()
no3 = data["no3"].to_numpy()

# Plotting
plt.figure(1)
gs = gridspec.GridSpec(3, 1)
plt.subplot(gs[0])
plt.scatter(time, salinity, c=floatnum, cmap='viridis', label='Salinity', alpha=0.5)
plt.title('Salinity')
plt.subplot(gs[1])
plt.scatter(time, pressure, c=floatnum, cmap='viridis', label='Pressure', alpha=0.5)
plt.title('Pressure')
plt.subplot(gs[2])
plt.scatter(time, temp, c=floatnum, cmap='viridis', label='Temperature', alpha=0.5)
plt.title('Temperature')
plt.tight_layout()

plt.figure(2)
gs = gridspec.GridSpec(2, 1)
plt.subplot(gs[0])
plt.scatter(time, doxyphase, c=floatnum, cmap='viridis', label='Phase Delay', alpha=0.5)
plt.title('Phase Delay')
plt.subplot(gs[1])
plt.scatter(time, doxytempv, c=floatnum, cmap='viridis', label='TempVolts', alpha=0.5)
plt.title('TempVolts')
plt.tight_layout()

plt.figure(3)
gs = gridspec.GridSpec(2, 1)
plt.subplot(gs[0])
plt.scatter(time, vrs, c=floatnum, cmap='viridis', label='pH vrs', alpha=0.5)
plt.title('pH vrs')
plt.subplot(gs[1])
plt.scatter(time, vk, c=floatnum, cmap='viridis', label='pH vk', alpha=0.5)
plt.title('pH vk')
plt.tight_layout()

plt.figure(4)
gs = gridspec.GridSpec(3, 1)
plt.subplot(gs[0])
plt.scatter(time, eco1, c=floatnum, cmap='viridis', label='ECO1', alpha=0.5)
plt.subplot(gs[1])
plt.scatter(time, eco2, c=floatnum, cmap='viridis', label='ECO2', alpha=0.5)
plt.subplot(gs[2])
plt.scatter(time, eco3, c=floatnum, cmap='viridis', label='ECO3', alpha=0.5)
plt.tight_layout()

plt.figure(5)
gs = gridspec.GridSpec(4, 1)
plt.subplot(gs[0])
plt.scatter(time, ocr1, c=floatnum, cmap='viridis', label='OCR1', alpha=0.5)
plt.subplot(gs[1])
plt.scatter(time, ocr2, c=floatnum, cmap='viridis', label='OCR2', alpha=0.5)
plt.subplot(gs[2])
plt.scatter(time, ocr3, c=floatnum, cmap='viridis', label='OCR3', alpha=0.5)
plt.subplot(gs[3])
plt.scatter(time, ocr4, c=floatnum, cmap='viridis', label='OCR4', alpha=0.5)
plt.tight_layout()

plt.figure(6)
plt.scatter(time, no3, c=floatnum, cmap='viridis', label='NO3', alpha=0.5)
plt.title('NO3 Plot')
plt.show()