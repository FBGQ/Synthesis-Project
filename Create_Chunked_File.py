import h5py
from datetime import datetime, timedelta
import PyQt6
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from scipy.interpolate import interp1d
# import cartopy.crs as ccrs
# from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
# import geopandas as gpd
from shapely.geometry import Point
import json
import os
from IPython.display import clear_output


#  ----------------------------------- FUNCTIONS ----------------------------------- #

def clear_output_notebook():
    clear_output(wait=True)

def open_file(file_name):
    file = h5py.File(file_name, 'r')
    return file

def read_ATL08(file_name):
    file = open_file(file_name)
    photon_h = file[beam + '/land_segments/canopy/h_canopy']
    delta_time = file[beam + '/land_segments/delta_time'] 

    photon_h = photon_h[:]
    delta_time = delta_time[:]

    return photon_h, delta_time



# FUNCTIONS

def find_consecutive_intervals(arr, threshold):
    """
    Find consecutive intervals of non-nan values in an array.
    Parameters
    ----------
    arr : numpy array
        Array to find consecutive intervals in.
    threshold : int
        Minimum length of consecutive interval to be returned.
    -------
    Returns
    -------
    intervals : list of tuples
        List of tuples containing the start and end indices of consecutive
        intervals.
    """ 
    non_nan_indices = np.where(~np.isnan(arr))[0]
    intervals = []
    start = non_nan_indices[0]
    count = 1

    for i in range(1, len(non_nan_indices)):
        if non_nan_indices[i] == non_nan_indices[i - 1] + 1:
            count += 1
        else:
            if count > threshold:
                intervals.append((start, non_nan_indices[i - 1]))
            start = non_nan_indices[i]
            count = 1
            

    # Check the last interval
    if count > threshold:
        intervals.append((start, non_nan_indices[-1]))
    
    if len(intervals) == 0:
        print("ERROR: There are no areas with",threshold,"consecutive data")
        return None
    else:
        print("There are", len(intervals), "areas with",threshold,"consecutive data")
        return intervals


def create_hdf5_file(filename):
    """
    Create an hdf5 file with the data from the ATL03 and ATL08 files.
    Parameters
    ----------
    filename : string
        Name of the file to be created.
    start : int
        Start index of the data to be saved.
    end : int
        End index of the data to be saved.
    -------
    Returns
    -------
    None.
    """
    # Create the file using the 'with' statement to ensure proper closing
    with h5py.File(filename, 'w') as f:
        # create the group
        group = f.create_group("canopy")

        # create the a subgroup for data coming from the ATL03 file
        ATL_03 = group.create_group("ATL03")
        # create the a subgroup for data coming from the ATL08 file
        ATL_08 = group.create_group("ATL08")

        # create the datasets
        ATL_03.create_dataset("delta_time", data=delta_time_03[idx_start:idx_end])
        ATL_03.create_dataset("photon_h", data=photon_h[idx_start:idx_end])
        ATL_03.create_dataset("dist", data=dist_03[idx_start:idx_end])
        #ATL_03.create_dataset("signal_conf_ph_land", data=signal_conf_ph_land[idx_start:idx_end])

        ATL_08.create_dataset("delta_time", data=delta_time_08[start:end])
        ATL_08.create_dataset("canopy_h", data=canopy[start:end])
        ATL_08.create_dataset("ground_h", data=ground_h[start:end])
        ATL_08.create_dataset("dist", data=dist_08[start:end])

    # The file is automatically closed when exiting the 'with' block


# ----------------------------------- MAIN ----------------------------------- #



# Read the variables from the JSON file
with open("variables.json", "r") as jsonfile:
    variables = json.load(jsonfile)

# Access the variables in the script
file_name_ATL08 = variables["file_name_ATL08"]
file_name_ATL03 = variables["file_name_ATL03"]
threshold = variables["threshold"]


# User inputs the beam

print("Select the beam you want to use: gt1l, gt1r, gt2l, gt2r, gt3l, gt3r")

beam = input("Enter the beam: ")
while beam not in ["gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"]:
    beam = input("Please enter one of the following options: gt1l, gt1r, gt2l, gt2r, gt3l, gt3r: ")


file = h5py.File(file_name_ATL08, 'r')

# Read ground data

ground = file[beam + '/land_segments/terrain/h_te_median']
ground_h = np.array(ground)
# To be changed
ground_h[ground_h>10000] = np.nan

# Read canopy height data

canopy = file[beam + '/land_segments/canopy/h_canopy']
canopy = np.array(canopy)
# To be changed
canopy[canopy > 10000] = np.nan

# Find consecutive intervals
# Known issue: not always true

intervals = find_consecutive_intervals(canopy, threshold)

print("Select the interval to plot:")
for i in range(len(intervals)):
    print(i, intervals[i])
    print("Max height:", np.nanmax(ground_h[intervals[i][0]:intervals[i][1]]))
    print("Min height:", np.nanmin(ground_h[intervals[i][0]:intervals[i][1]]))
    print("Delta:", np.nanmax(ground_h[intervals[i][0]:intervals[i][1]]) - np.nanmin(ground_h[intervals[i][0]:intervals[i][1]]), "m")
    print("")
selected_interval = (input())
while not selected_interval.isdigit():
    selected_interval = input("Please enter a valid option: ")
while int(selected_interval) not in range(len(intervals)):
    selected_interval = input("Please enter select an interval between 0 and: " + str(len(intervals)-1) + ": ")

selected_interval = int(selected_interval)

# Clear Jupyter Notebook cell output
clear_output_notebook()

print(f"Selected interval: {intervals[selected_interval][0]} - {intervals[selected_interval][1]}")
print("Max height:", np.nanmax(ground_h[intervals[selected_interval][0]:intervals[selected_interval][1]]))
print("Min height:", np.nanmin(ground_h[intervals[selected_interval][0]:intervals[selected_interval][1]]))
print("Delta Ground:", np.nanmax(ground_h[intervals[selected_interval][0]:intervals[selected_interval][1]]) - np.nanmin(ground_h[intervals[selected_interval][0]:intervals[selected_interval][1]]), "m")




# ----------------------------------- PLOT ----------------------------------- #

# select start and end of the interval

if intervals == None: 
    start = 0
    end = len(canopy) - 1
else:
    start = intervals[selected_interval][0]
    end = intervals[selected_interval][1]

# Read time data
epoch_time = datetime(2018, 1, 1, 0, 0)
delta_time_08 = file[beam + '/land_segments/delta_time']
delta_time_08 = np.array(delta_time_08)

lat_08 = file[beam + '/land_segments/latitude']
lat_08 = np.array(lat_08)

lon_08 = file[beam + '/land_segments/longitude']
lon_08 = np.array(lon_08)

lon_08 = lon_08[start:end]
lat_08 = lat_08[start:end]

start_t_08 = delta_time_08[start]
end_t_08 = delta_time_08[end]

# Generate date_data_can for the selected interval
date_data_can = []
for i in range(start, end):
    date_data_can.append(epoch_time + timedelta(seconds=delta_time_08[i]))

dist_08 = (delta_time_08[start:end] - delta_time_08[start]) * 7.2 

# Plot the canopy height
# plt.figure(figsize=(15, 5))
# plt.scatter(date_data_can, canopy[start:end] + ground_h[start:end], s=6)
# plt.scatter(date_data_can, ground_h[start:end], s=6)
# plt.grid(linestyle='--', linewidth=0.5)
# plt.title('Canopy Height')
# plt.legend(['Canopy Height', 'Ground Height'])
# plt.xlabel('Time')
# plt.ylabel('Height (m)')
# plt.show()

# plot the canopy height and the ground height as function of the distance
plt.figure(figsize=(15, 5))
plt.scatter(dist_08, canopy[start:end] + ground_h[start:end], s=6)
plt.scatter(dist_08, ground_h[start:end], s=6)
plt.grid(linestyle='--', linewidth=0.5)
plt.title('Canopy Height')
plt.legend(['Canopy Height', 'Ground Height'])
plt.xlabel('Distance (km)')
plt.ylabel('Height (m)')
plt.show()

file.close()

# ---------------------------------------------------------------------------- #


# ----------------------------------- ATL03 ----------------------------------- #

# Read ATL03 data

filename = file_name_ATL03
file = h5py.File(filename, 'r')

photon_h = np.array(file[beam + '/heights/h_ph'])
delta_time_03 = file[beam +'/heights/delta_time']
delta_time_03 = np.array(delta_time_03)

start_t = delta_time_08[0]
end_t = delta_time_08[-1]

lat_03 = file[beam + '/heights/lat_ph']
lat_03 = np.array(lat_03)

lon_03 = file[beam + '/heights/lon_ph']
lon_03 = np.array(lon_03)

# subtract the first time of ATL08 from the time of ATL03
delta_time_03_s = delta_time_03 - start_t_08

# find the index of the closest value to 0
idx_start = (np.abs(delta_time_03_s - 0)).argmin()

# subtract the last time of ATL08 from the time of ATL03
delta_time_03_e = delta_time_03 - end_t_08
# find the index of the closest value to 0
idx_end = (np.abs(delta_time_03_e - 0)).argmin()


lat_03 = lat_03[idx_start:idx_end]
lon_03 = lon_03[idx_start:idx_end]

dist_03 = (delta_time_03[idx_start:idx_end] - delta_time_03[idx_start]) * 7.2

# generate date_data_ph for the selected interval
date_data_ph = []
for i in range(idx_start, idx_end):
    date_data_ph.append(epoch_time + timedelta(seconds=delta_time_03[i]))

plt.figure(figsize=(15, 5))
plt.scatter(dist_03, photon_h[idx_start:idx_end], s=0.5, c='gray')
plt.scatter(dist_08, canopy[start:end] + ground_h[start:end], s=6, c='blue')
plt.scatter(dist_08, ground_h[start:end], s=6, c='orange')
plt.grid(linestyle='--', linewidth=0.5)
plt.ylim(np.nanmin(ground_h[start:end]) - 5, np.nanmax(ground_h[start:end] + canopy[start:end]) + 5)
plt.xlabel('Distance (km)')
plt.ylabel('Height (m)')
plt.legend(['Photon Height - ATL03', 'Canopy Height - ATL08', 'Ground Height - ATL08'])
plt.title('Photon Height')
plt.show()

while True:
    if os.path.exists('chunked_canopy.hdf5'):
        print("A file with the name chunked_canopy.hdf5 already exists in the folder.")
        print("Do you want to overwrite it? (y/n)")
        overwrite = input().lower()  

        if overwrite == 'y':
            create_hdf5_file('chunked_canopy.hdf5')
            print("The file was overwritten.")
            break  
        elif overwrite == 'n':
            print("The file was not overwritten.")
            break  
        else:
            print("ERROR: Please enter y or n")
    else:
        create_hdf5_file('chunked_canopy.hdf5')
        print("Chunked File containing only the selected interval was created.")
        break 


file.close()
