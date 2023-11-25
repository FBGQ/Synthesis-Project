import h5py
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import json



filename = "chunked_canopy.hdf5"
file = h5py.File(filename, 'r')

photon_h = file['canopy/ATL03/photon_h']
delta_time = file['canopy/ATL03/delta_time'] 

photon_h = photon_h[:]
delta_time = delta_time[:]


delta_time = delta_time - delta_time[0]
dist = delta_time * 7.2

plt.figure(figsize=(15, 5))
plt.plot(dist * 1000, photon_h, '.', color='green', markersize=1.2)
plt.title('Original ATL03 data')
plt.xlabel('Distance [m]')
plt.ylabel('Photon Height [m]')
plt.grid()
plt.show()

dist_m = dist * 1000


interval_ground = 20
interval_vertical = 1.5

#print(dist_m[interval_low:interval_high].min())
binx = np.arange(dist_m.min(), (dist_m.max()), interval_ground)
biny = np.arange((photon_h.min()), (photon_h.max()), interval_vertical)

#print((binx))
#print((biny))

ret = stats.binned_statistic_2d(dist_m, photon_h, None,statistic='count', bins=[binx, biny])


# Create a list to store the top 5 values and their indices for each row
top_values_and_indices = []

# Set the threshold value
threshold = 0

# Iterate through each row in the matrix
for row in ret.statistic:
    top_values, indices = [], []
    found_below_threshold = False
    
    # Get the indices of the top 4 values
    sorted_indices = np.argsort(row)[-2:][::-1]
    
    for idx in sorted_indices:
        value = row[idx]
        if value < threshold and not found_below_threshold:
            found_below_threshold = True
            top_values.append(np.nan)
            indices.append(np.nan)
        else:
            top_values.append(value)
            indices.append(idx)
        
    # Fill remaining slots with NaN if threshold is found
    while len(top_values) < 2:
        top_values.append(np.nan)
        indices.append(np.nan)
    
    # Sort top_values and indices based on top_values in descending order
    sorted_indices = np.argsort(top_values)[::-1]
    top_values = [top_values[i] for i in sorted_indices]
    indices = [indices[i] for i in sorted_indices]
    
    # Store the top 5 values and their indices in the list
    top_values_and_indices.append((top_values, indices))


    # from top_values and indices, generates an array with only the indices
index = []
for i in range(len(top_values_and_indices)):
    index.append(top_values_and_indices[i][1][0])

ground_ph = np.array([])


edge_x0 = int(binx[0])
edge_x1 = int(binx[1])


edge_y0 = int(biny[0]) + index[0]*interval_vertical
edge_y1 = int(biny[1]) + index[0]*interval_vertical

myphotons = photon_h[(dist_m > edge_x0) & (dist_m < edge_x1) & (photon_h > edge_y0) & (photon_h < edge_y1)]

ground_ph = np.array([])
kept_dist_m_values = np.array([])  # New array to store kept dist_m values

for i in range(len(binx) - 1):
    edge_x0 =  interval_ground * i
    edge_x1 =  interval_ground * (i + 1)

    edge_y0 = photon_h.min() + interval_vertical * index[i]
    edge_y1 = photon_h.min() + interval_vertical * (index[i] + 1)

    temp_dist_m_values = dist_m[(photon_h >= edge_y0) & (photon_h < edge_y1) & (dist_m >= edge_x0) & (dist_m <= edge_x1)]
    temp_ground_ph = photon_h[(photon_h >= edge_y0) & (photon_h < edge_y1) & (dist_m >= edge_x0) & (dist_m <= edge_x1)]

    # Append the kept dist_m values to the new variable
    kept_dist_m_values = np.append(kept_dist_m_values, temp_dist_m_values)
    
    ground_ph = np.append(ground_ph, temp_ground_ph)

plt.figure(figsize=(15, 5))
plt.plot(kept_dist_m_values, ground_ph, '.', color='green', markersize=1.2)
plt.xlabel('Distance [m]')
plt.ylabel('Photon Height [m]')
plt.ylim(ground_ph.min() -10, ground_ph.max() + 10)
plt.title('Photons identified as ground photons')
plt.grid()
plt.show()

with open('variables.json', 'r') as json_file:
    variables = json.load(json_file)

variables['kept_dist_m_values'] = kept_dist_m_values.tolist()
variables['ground_ph'] = ground_ph.tolist()

variables['dist_m'] = dist_m.tolist()
variables['photon_h'] = photon_h.tolist()

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)

file.close()
