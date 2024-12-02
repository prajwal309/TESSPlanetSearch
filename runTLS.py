import numpy as np
import matplotlib.pyplot as plt
from wotan import flatten
from astropy.timeseries import LombScargle
from astropy.io import fits
from astropy.timeseries import BoxLeastSquares
import glob
import os
import sys
from scipy.stats import binned_statistic

TIC_ID = sys.argv[1]
print("The TIC ID is given by: ", TIC_ID)

SubFolder = "./TESSData/TIC" + TIC_ID

# get all the fits file in a directory and its subdirectories
allFitsFiles = glob.glob(os.path.join(SubFolder, '**', '*.fits'), recursive=True)

AllTime = []
AllFlux = []
Time2Plot = []
Flux2Plot = []
for fitsFile in allFitsFiles:
    if not("a_fast") in fitsFile:
        print("Considering only *a_fast* files")
        continue

    # Open the fits file
    fileContents = fits.open(fitsFile)

    Time = fileContents[1].data['TIME']
    Flux = fileContents[1].data['PDCSAP_FLUX']
    Quality = fileContents[1].data['QUALITY']
    fileContents.close()

    #Remove NaNs
    removeIndex = np.logical_or(np.isnan(Flux), Quality!=0)
    currentTime = Time[~removeIndex]
    currentFlux = Flux[~removeIndex]
    currentFlux = currentFlux/np.nanmedian(currentFlux)

    AllTime.extend(currentTime)
    AllFlux.extend(currentFlux)
    Time2Plot.append(currentTime)
    Flux2Plot.append(currentFlux)

#Convert to numpy arrays
AllTime = np.array(AllTime)
AllFlux = np.array(AllFlux)


#sort the arrays
sortIndexes = np.argsort(AllTime)
AllTime = AllTime[sortIndexes]
AllFlux = AllFlux[sortIndexes]

#Now flatten the light curve
flatten_lc, trend_lc = flatten(AllTime, AllFlux, method='biweight', window_length=0.35, break_tolerance=0.5, return_trend=True)



# Run Box Least Squares
print("Now running Box Least Squares")
model = BoxLeastSquares(AllTime, flatten_lc)

periods = np.linspace(0.25, 30, 1000)
periodogram = model.power(periods, 0.2)

# Find the best period
best_period = periodogram.period[np.argmax(periodogram.power)]
print(f"Best period: {best_period} days")
# Combine the plots together


fig, axs = plt.subplots(3, 1, figsize=(10, 15))

refTimeOG = np.min(Time2Plot[0])
# Plot the original data and trend
for i in range(len(Time2Plot)):
    if i==0:
        offset = np.min(Time2Plot[i])
    else:
        offset = np.min(Time2Plot[i]) - (np.max(Time2Plot[i-1])-np.min(Time2Plot[i-1]))-0.5
    axs[0].plot(Time2Plot[i]-offset, Flux2Plot[i], linestyle="None", marker=".",  label=f'LC {i}')
    currentTrendLC = np.interp(Time2Plot[i], AllTime, trend_lc)
    if i==0:
        axs[0].plot(Time2Plot[i]-offset, currentTrendLC, 'r-', label='Trend')
    else:
        axs[0].plot(Time2Plot[i]-offset, currentTrendLC, 'r-')
axs[0].set_xlabel('Time')
axs[0].set_ylabel('Flux')
axs[0].legend()
axs[0].set_title('Original Light Curve and Trend')

# Plot the BLS results
axs[1].plot(periodogram.period, periodogram.power, 'k-')
axs[1].set_xlabel('Period (days)')
axs[1].set_ylabel('Power')
#axs[1].set_title('Box Least Squares Periodogram')

phase = (AllTime % best_period) / best_period

#arrange flux values in phase order
phaseSortOrder = np.argsort(phase)
phase = phase[phaseSortOrder]
fluxPhase = flatten_lc[phaseSortOrder]


binnedTime = binned_statistic(phase, phase, bins=300, statistic='mean')[0]
binnedFlux = binned_statistic(phase, fluxPhase, bins=300, statistic='median')[0]

# Phase fold the light curve on the best period
axs[2].plot(phase, flatten_lc, 'k.')
axs[2].plot(binnedTime, binnedFlux, 'gd')
axs[2].set_xlabel('Phase')
axs[2].set_ylabel('Flux')
#axs[2].set_title('Phase Folded Light Curve')

plt.tight_layout()
plt.savefig("figures/" + TIC_ID + '_BLS.png')
plt.show()