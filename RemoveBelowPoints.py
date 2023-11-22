import h5py
import scipy
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json


with open('variables.json') as json_file:
    variables = json.load(json_file)

kept_dist_m_values_temp = variables['kept_dist_m_values_temp']
ground_ph_temp = variables['ground_ph_temp']
photon_h = variables['photon_h']
dist_m = variables['dist_m']

kept_dist_m_values_temp = np.array(kept_dist_m_values_temp)
ground_ph_temp = np.array(ground_ph_temp)
photon_h = np.array(photon_h)
dist_m = np.array(dist_m)


# Calculate the differences between consecutive points
differences = [kept_dist_m_values_temp[i + 1] - kept_dist_m_values_temp[i] for i in range(len(kept_dist_m_values_temp) - 1)]

# # Calculate the average distance
# average_distance = sum(differences) / len(differences)

# print("Average Distance between Points:", average_distance)


# List to store pairs of indices where differences are bigger than 5
large_difference_pairs = []

# Iterate through differences and store pairs of indices where difference is bigger than 5
start_index = None
for i in range(len(differences)):
    if differences[i] > 10:
        if start_index is None:
            start_index = i
    elif start_index is not None:
        large_difference_pairs.append([start_index, i])
        start_index = None

# If a large difference extends to the end, include it in the pairs
if start_index is not None:
    large_difference_pairs.append([start_index, len(differences)])


j = 0
filtered_data = []

for i in range(len(ground_ph_temp) - 1):

    x1 = kept_dist_m_values_temp[i]
    x2 = kept_dist_m_values_temp[i+1]

    y1 = ground_ph_temp[i]
    y2 = ground_ph_temp[i+1]

    # check if x1 and x2 are the same
    if x1 == x2:
        if photon_h[j] > y1:
            filtered_data.append((x1, photon_h[j]))
        j = j + 1
        # skip to next iteration
        continue
    
    # line equation
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    while(dist_m[j] < x2):
        if photon_h[j] > (m * dist_m[j] + b):
            filtered_data.append((dist_m[j], photon_h[j]))
        j = j + 1

# plot filtered data

filtered_data = np.array(filtered_data)

plt.figure(figsize=(15, 5))
plt.plot(filtered_data[:,0], filtered_data[:,1], '.', color='green', markersize=1.2)
plt.xlabel('dist [m]')
plt.ylabel('photon_h')
plt.ylim(ground_ph_temp.min() -10, ground_ph_temp.max() + 10)
plt.grid()
plt.show()

above_ground_ph = filtered_data[:,1]
above_ground_dist_m = filtered_data[:,0]

# tilde = ~
cond = ~np.isin(above_ground_ph, ground_ph_temp)
above_ground_ph = above_ground_ph[cond]
above_ground_dist_m = above_ground_dist_m[cond]

median_plt = np.median(above_ground_ph)
std_dev_ph = np.std(above_ground_ph)

# plot above ground data
plt.figure(figsize=(15, 5))
plt.plot(above_ground_dist_m, above_ground_ph, '.', color='green', markersize=1.2)
plt.xlabel('dist [m]')
plt.ylabel('photon_h')
plt.ylim(above_ground_ph.min() - 10, median_plt + std_dev_ph)
plt.grid()
plt.show()


with open('variables.json', 'r') as json_file:
    variables = json.load(json_file)

variables['above_ground_dist_m'] = above_ground_dist_m.tolist()
variables['above_ground_ph'] = above_ground_ph.tolist()

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)



