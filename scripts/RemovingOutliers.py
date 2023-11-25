import h5py
import scipy
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from scipy.spatial import cKDTree
import numpy as np

# import variables

with open('variables.json') as json_file:
    variables = json.load(json_file)

kept_dist_m_values = variables['kept_dist_m_values']
ground_ph = variables['ground_ph']
dist_m = variables['dist_m']
photon_h = variables['photon_h']


# Assuming you have x_centers, y_centers, photon_h, and dist_m defined

x_centers = kept_dist_m_values
y_centers = ground_ph

# Create a KDTree using the centers
tree = cKDTree(np.c_[dist_m, photon_h])

# Create a list to store the filtered points
filtered_points = []

# Query points within a radius around each center and store the filtered points
for i in range(len(x_centers)):
    indices = tree.query_ball_point((x_centers[i], y_centers[i]), r=1)
    filtered_points.extend([(photon_h[j], dist_m[j]) for j in indices])

# Now, filtered_points contains the (x, y) coordinates from photon_h and dist_m arrays
# that are within radius 1 of each center defined by x_centers and y_centers.

ground_ph = np.array(filtered_points)[:,0]
kept_dist_m_values = np.array(filtered_points)[:,1]

# Gaussian smoothing

from scipy.ndimage import gaussian_filter1d
temp_old = ground_ph  # first step
kept_dist_m_values_temp = kept_dist_m_values
ground_ph_temp = ground_ph
from scipy import stats

i = 0


while(1):
    
        # Gaussian smoothing

        std_dev_ph = np.std(temp_old)
        
        # Smooth the data
        smoothed_ground_ph = gaussian_filter1d(temp_old, sigma=std_dev_ph)
        diff = temp_old - smoothed_ground_ph

        # remove outliers
        z = np.abs(stats.zscore(diff))
        threshold = std_dev_ph
        # print(np.where(z > threshold))
    
        # The first array contains the list of row numbers and second array respective column numbers
        outliers = np.where(z > threshold)
    
        # Remove the outliers
        if len(outliers[0]) > 0:
                kept_dist_m_values_temp = np.delete(kept_dist_m_values_temp, outliers[0])
                ground_ph_temp = np.delete(ground_ph_temp, outliers[0])
                removed_points = True
        else:
                removed_points = False

        # break if no points are removed or after 100 iterations
        if not removed_points or i > 10:
                break
    
        i = i + 1
        
        temp_old = ground_ph_temp

# plot new ground_ph

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(15, 5))
fig.suptitle('Vertically stacked subplots')

ax1.plot(kept_dist_m_values, ground_ph, '.', color='green', markersize=1.2)
ax1.set_ylim(ground_ph.min() - 10, ground_ph.max() + 10)
ax1.set_ylabel('photon_h')  # Set the y-axis label for ax1
ax1.grid()

ax2.plot(kept_dist_m_values_temp, ground_ph_temp, '.', color='green', markersize=1.2)
ax2.set_ylim(ground_ph_temp.min() - 10, ground_ph_temp.max() + 10)
ax2.set_xlabel('dist [m]')  # Set the x-axis label for ax2
ax2.set_ylabel('photon_h')  # Set the y-axis label for ax2
ax2.grid()

plt.show()

# plot photon_h and the interval with these values
plt.figure(figsize=(15, 5))
plt.plot(dist_m, photon_h, '.', color='green', markersize=1.2)
plt.plot(kept_dist_m_values_temp, ground_ph_temp, '.', color='red', markersize=1.2)
plt.xlabel('dist [m]')
plt.ylabel('photon_h')
plt.ylim(ground_ph_temp.min() -10, ground_ph_temp.max() + 10)
plt.grid()
plt.show()



with open('variables.json', 'r') as json_file:
    variables = json.load(json_file)

variables['kept_dist_m_values_temp'] = kept_dist_m_values_temp.tolist()
variables['ground_ph_temp'] = ground_ph_temp.tolist()

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)

