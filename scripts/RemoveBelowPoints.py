import h5py
import scipy
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

with open('variables.json') as json_file:
    variables = json.load(json_file)

kept_dist_m_values_temp = np.array(variables['kept_dist_m_values_temp'])
ground_ph_temp = np.array(variables['ground_ph_temp'])
photon_h = np.array(variables['photon_h'])
dist_m = np.array(variables['dist_m'])

# Calculate the differences between consecutive points
differences = np.diff(kept_dist_m_values_temp)

# List to store pairs of indices where differences are bigger than 10
large_difference_pairs = []

# Iterate through differences and store pairs of indices where difference is bigger than 10
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
    x1, x2 = kept_dist_m_values_temp[i], kept_dist_m_values_temp[i + 1]
    y1, y2 = ground_ph_temp[i], ground_ph_temp[i + 1]

    # check if x1 and x2 are the same
    if x1 == x2:
        if j < len(photon_h) and photon_h[j] > y1:
            filtered_data.append((x1, photon_h[j]))
        j += 1
        continue

    # line equation
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    while j < len(dist_m) and dist_m[j] < x2:
        if photon_h[j] > (m * dist_m[j] + b):
            filtered_data.append((dist_m[j], photon_h[j]))
        j += 1

# plot filtered data
filtered_data = np.array(filtered_data)

above_ground_ph = filtered_data[:, 1]
above_ground_dist_m = filtered_data[:, 0]

# tilde = ~
cond = ~np.isin(above_ground_ph, ground_ph_temp)
above_ground_ph = above_ground_ph[cond]
above_ground_dist_m = above_ground_dist_m[cond]

median_plt = np.median(above_ground_ph)
std_dev_ph = np.std(above_ground_ph)

# plot above ground data
plt.figure(figsize=(15, 5))
plt.plot(above_ground_dist_m, above_ground_ph, '.', color='green', markersize=1.2)
plt.xlabel('Distance [m]')
plt.ylabel('Photon Height [m]')
plt.ylim(above_ground_ph.min() - 10, median_plt + std_dev_ph)
plt.title('Photons above ground')
plt.grid()
plt.show()

# Update variables and save to JSON file
variables['above_ground_dist_m'] = above_ground_dist_m.tolist()
variables['above_ground_ph'] = above_ground_ph.tolist()

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)
