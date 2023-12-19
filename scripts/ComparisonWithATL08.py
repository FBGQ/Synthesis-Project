import json
import h5py
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -------   1   --------- Read ATL08 data

filename = "chunked_canopy.hdf5"
file = h5py.File(filename, 'r')

photon_h_ATL08 = file['canopy/ATL08/canopy_h']
delta_time_ATL08 = file['canopy/ATL08/delta_time'] 
ground_h_ATL08 = file['canopy/ATL08/ground_h']

photon_h_ATL08 = photon_h_ATL08[:]
delta_time = delta_time_ATL08[:]

delta_time = delta_time - delta_time[0]
dist_ATL08 = delta_time * 7.2
dist_ATL08 = dist_ATL08 * 1000

ground_h_ATL08 = ground_h_ATL08[:]

file.close()


# -------   2   --------- Read JSON file

with open('variables.json') as json_file:
    variables = json.load(json_file)

dist_m = variables['dist_m']
photon_h = variables['photon_h']

h_max = variables['h_max']
shifted_h_max_dist = variables['shifted_h_max_dist']
ground_mean = variables['ground_mean']
valid_ground_mean = variables['valid_ground_mean']
valid_h_max = variables['valid_h_max']
varPlot_h_max = variables['varPlot_h_max']

varPlot_h_max = np.array(varPlot_h_max)

valid_ground_mean = np.array(valid_ground_mean)
valid_h_max = np.array(valid_h_max)

# compare ground_mean and h_max. If ground_mean is nan, h_max is also nan
for i in range(len(valid_ground_mean)):
    if np.isnan(valid_ground_mean[i]):
        valid_h_max[i] = np.nan
        shifted_h_max_dist[i] = np.nan


# -------   3   --------- Plot comparison

plt.figure(figsize=(20, 10))
plt.plot(dist_m, photon_h, '.', color='gray', markersize=1.2)
plt.plot(dist_ATL08, ground_h_ATL08 + photon_h_ATL08, 's', color='green', markersize=5)
plt.plot(dist_ATL08, ground_h_ATL08, 's', color='orange', markersize=5)
plt.plot(shifted_h_max_dist, valid_h_max, '.', color='red', markersize=8)
plt.plot(shifted_h_max_dist, valid_ground_mean, '.', color='blue', markersize=8)
plt.ylim(valid_ground_mean.min() - 10, varPlot_h_max.max() + 10)
plt.legend(['ATL03 Photon Cloud','ATL08 - Canopy', 'ATL08 - Ground', 'Estimated Canopy', 'Estimated Ground'])
plt.xlabel('dist [m]')
plt.ylabel('Photon Height [m]')
plt.title('Comparison between estimated height with original ATL08 product')
plt.grid()
plt.show()


# -------   4   --------- Print means

# Print mean of ATL08 ground_h
print('Mean of ATL08 ground_h: ', np.nanmean(ground_h_ATL08),'[m]','----', 'Mean of ground_mean: ', np.nanmean(ground_mean),'[m]')

print('\n')

# print mean of ATL08 ground_h + ATL08 canopy_h
print('Mean of ATL08 canopy_h: ', np.nanmean(photon_h_ATL08),'[m]', '----', 'Mean of h_max: ', np.nanmean(valid_h_max - valid_ground_mean),'[m]')
