import h5py
import scipy
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from scipy.spatial import cKDTree
from IPython.display import clear_output

def clear_output_notebook():
    clear_output(wait=True)

with open('variables.json') as json_file:
    variables = json.load(json_file)

user_quality_flags = variables['user_quality_flags']
segment = variables['segment']

canopy_flag_dist = variables['canopy_flag_dist']
canopy_flag = variables['canopy_flag']

above_ground_dist_m = variables['above_ground_dist_m']
above_ground_ph = variables['above_ground_ph']

kept_dist_m_values_temp = variables['kept_dist_m_values_temp']
ground_ph_temp = variables['ground_ph_temp']    

dist_m = variables['dist_m']
photon_h = variables['photon_h']

dist_m = np.array(dist_m)
photon_h = np.array(photon_h)
above_ground_dist_m = np.array(above_ground_dist_m)
above_ground_ph = np.array(above_ground_ph)
canopy_flag_dist = np.array(canopy_flag_dist)
canopy_flag = np.array(canopy_flag)
kept_dist_m_values_temp = np.array(kept_dist_m_values_temp)
ground_ph_temp = np.array(ground_ph_temp)

tree = cKDTree(np.c_[canopy_flag_dist, canopy_flag])

quality_flag = np.zeros(len(canopy_flag))  # Initialize quality_flag array

for i in range(len(canopy_flag)):
    middle_kd_start = canopy_flag[i]
    middle_kd_start_dist = canopy_flag_dist[i]
    distances, indices = tree.query([[middle_kd_start_dist, middle_kd_start]], k=3)

    if (distances[0][1] < 5) and (distances[0][2] < 5):
        quality_flag[i] = 1
    elif 5 <= distances[0][1] < 10:
        quality_flag[i] = 2
    else:
        quality_flag[i] = 3

# Plot the photons with quality_flag = 1

plt.figure(figsize=(15, 5))
# plt.plot(above_ground_dist_m, above_ground_ph, '.', color='green', markersize=1)
plt.plot(canopy_flag_dist[quality_flag == 1], canopy_flag[quality_flag == 1], '.', color='red', markersize=5)
plt.plot(canopy_flag_dist[quality_flag == 2], canopy_flag[quality_flag == 2], 'x', color='blue', markersize=5)
plt.plot(canopy_flag_dist[quality_flag == 3], canopy_flag[quality_flag == 3], '^', color='gray', markersize=5)
plt.xlabel('dist [m]')
plt.ylabel('photon_h')
plt.ylim(above_ground_ph.min() -10, above_ground_ph.max() + 10)
plt.grid()
plt.show()




# Assuming above_ground_dist_m, above_ground_ph, canopy_flag_dist, canopy_flag, and quality_flag are already defined

h_max = []
h_max_dist = []
ground_mean = []

for i in range(int(np.floor(canopy_flag_dist.max() / segment))):
    # Define the range for the current segment
    segment_range = np.logical_and(i * segment <= canopy_flag_dist, canopy_flag_dist <= (i + 1) * segment)

    # Select data within the current segment
    canopy_flag_dist_seg = canopy_flag_dist[segment_range]
    canopy_flag_seg = canopy_flag[segment_range]
    quality_flag_seg = quality_flag[segment_range]

    # Max height with user-specified quality flags for the current segment
    selected_flags = np.isin(quality_flag_seg, np.nonzero(user_quality_flags)[0] + 1)
    canopy_flag_seg_selected = canopy_flag_seg[selected_flags]

    if len(canopy_flag_seg_selected) == 0:
        h_max.append(np.nan)
        h_max_dist.append(segment * i)
    else:
        h_max.append(canopy_flag_seg_selected.max())
        h_max_dist.append(segment * i)

    # Ground mean for the current segment
    segment_range_ground = np.logical_and(i * segment <= kept_dist_m_values_temp, kept_dist_m_values_temp <= (i + 1) * segment)
    kept_dist_m_values_temp_seg = kept_dist_m_values_temp[segment_range_ground]
    ground_ph_temp_seg = ground_ph_temp[segment_range_ground]

    if len(ground_ph_temp_seg) == 0:
        ground_mean.append(np.nan)
    else:
        ground_mean.append(np.mean(ground_ph_temp_seg))

# Convert lists to NumPy arrays
h_max = np.array(h_max)
h_max_dist = np.array(h_max_dist)
ground_mean = np.array(ground_mean)

# Remove NaN values and corresponding distances
#valid_ground_mean = ground_mean[~np.isnan(ground_mean)]
#valid_h_max_dist = h_max_dist[~np.isnan(ground_mean)]
#valid_h_max = h_max[~np.isnan(ground_mean)]

#valid_h_max = valid_h_max[~np.isnan(valid_h_max)]
#valid_h_max_dist = valid_h_max_dist[~np.isnan(valid_h_max)]
#valid_ground_mean = valid_ground_mean[~np.isnan(valid_ground_mean)]

# remove values where ground_mean is nan so that we can plot the graph
valid_ground_mean = []
valid_h_max_dist = []
valid_h_max = []

for i in range(len(ground_mean)):
    if np.isnan(ground_mean[i]):
        continue
    else:
        valid_ground_mean.append(ground_mean[i])
        valid_h_max_dist.append(h_max_dist[i])
        valid_h_max.append(h_max[i])

valid_ground_mean = np.array(valid_ground_mean)
valid_h_max_dist = np.array(valid_h_max_dist)
valid_h_max = np.array(valid_h_max)

varPlot_h_max = np.array(valid_h_max)
varPlot_h_max = varPlot_h_max[~np.isnan(varPlot_h_max)]

offset = segment/2  # You can adjust this value based on your preference
shifted_h_max_dist = valid_h_max_dist + offset

# Plot the max height for each segment
plt.figure(figsize=(15, 5))
plt.plot(dist_m, photon_h, '.', color='gray', markersize=1.2)
plt.plot(shifted_h_max_dist, valid_ground_mean, '.', color='blue', markersize=5)
plt.plot(shifted_h_max_dist, valid_h_max, '.', color='red', markersize=5)
plt.xlabel('Distance')
plt.ylabel('Max Height')
plt.ylim(valid_ground_mean.min() - 10, varPlot_h_max.max() + 10)
plt.grid()
plt.show()


with open('variables.json', 'r') as json_file:
    variables = json.load(json_file)

variables['h_max'] = h_max.tolist()
variables['h_max_dist'] = h_max_dist.tolist()
variables['ground_mean'] = ground_mean.tolist()
variables['valid_h_max'] = valid_h_max.tolist()
variables['valid_ground_mean'] = valid_ground_mean.tolist()
variables['shifted_h_max_dist'] = shifted_h_max_dist.tolist()
variables['varPlot_h_max'] = varPlot_h_max.tolist()

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)
