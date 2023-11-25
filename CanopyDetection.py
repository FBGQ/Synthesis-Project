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


interval_ground = 20
interval_vertical = 8

with open('variables.json') as json_file:
    variables = json.load(json_file)

above_ground_dist_m = variables['above_ground_dist_m']
above_ground_ph = variables['above_ground_ph']

above_ground_dist_m = np.array(above_ground_dist_m)
above_ground_ph = np.array(above_ground_ph)

#print(dist_m[interval_low:interval_high].min())
binx = np.arange(above_ground_dist_m.min(),above_ground_dist_m.max(), interval_ground)
biny = np.arange(above_ground_ph.min(), above_ground_ph.max(), interval_vertical)

#print((binx))
#print((biny))

ret = stats.binned_statistic_2d(above_ground_dist_m, above_ground_ph, None,statistic='count', bins=[binx, biny])

canopy_flag = np.array([])
canopy_flag_dist = np.array([])

for i in range(len(ret.statistic)):

    bin = ret.statistic[i, :]

    indices_above_mean = np.where(bin > np.nanmean(bin[bin != 0]))[0]

    # Check if there are any elements above the mean
    if len(indices_above_mean) == 0:
        # If no bin has a value above the mean, continue to the next iteration
        continue

    top_bin = indices_above_mean[-1]

    edge_y0 = biny[top_bin]
    edge_y1 = biny[top_bin + 1]
    edge_x0 = binx[i]
    edge_x1 = binx[i + 1]
    above_ground_ph_top_bin = above_ground_ph[(above_ground_ph >= edge_y0) & (above_ground_ph < edge_y1) & (above_ground_dist_m >= edge_x0) & (above_ground_dist_m <= edge_x1)]
    middle_kd_start = np.median(above_ground_ph_top_bin)
    middle_kd_start_dist = np.median(above_ground_dist_m[(above_ground_ph >= edge_y0) & (above_ground_ph < edge_y1) & (above_ground_dist_m >= edge_x0) & (above_ground_dist_m <= edge_x1)])
    tree = cKDTree(np.c_[above_ground_dist_m, above_ground_ph])
    distances, indices = tree.query([[middle_kd_start_dist, middle_kd_start]], k=20)

    if np.any(distances > 10): 
        continue
    else:
        
        canopy_flag = np.append(canopy_flag, above_ground_ph[indices])
        canopy_flag_dist = np.append(canopy_flag_dist, above_ground_dist_m[indices])
        continue



# Plot the canopy_flag
# plt.figure(figsize=(15, 5))
# plt.plot(above_ground_dist_m, above_ground_ph, '.', color='green', markersize=1)
# plt.plot(canopy_flag_dist, canopy_flag, '.', color='red', markersize=1)
# plt.xlabel('dist [m]')
# plt.ylabel('photon_h')
# plt.ylim(above_ground_ph.min() -10, above_ground_ph.max() + 10)
# plt.grid()
# plt.show()



# Now we take an estimate of the tree height

above_ground_dist_m = above_ground_dist_m[above_ground_ph < canopy_flag.max() + 30]
above_ground_ph = above_ground_ph[above_ground_ph < canopy_flag.max() + 30]

interval_ground = 20
interval_vertical = 8

#print(dist_m[interval_low:interval_high].min())
binx = np.arange(above_ground_dist_m.min(),above_ground_dist_m.max(), interval_ground)
biny = np.arange(above_ground_ph.min(), above_ground_ph.max(), interval_vertical)

#print((binx))
#print((biny))

ret = stats.binned_statistic_2d(above_ground_dist_m, above_ground_ph, None,statistic='count', bins=[binx, biny])


# store the first bin in an array

first_bin = ret.statistic[0,:]

# take the last index that is above the mean

top_fst_bin = np.where(first_bin > np.nanmean(first_bin[first_bin != 0]))[0][-1]


# y edges of the top_fst_bin

edge_y0 = biny[top_fst_bin]
edge_y1 = biny[top_fst_bin + 1]

edge_x0 = binx[0]
edge_x1 = binx[1]


# access above_ground_ph that are in the top_fst_bin

above_ground_ph_top_fst_bin = above_ground_ph[(above_ground_ph >= edge_y0) & (above_ground_ph < edge_y1) & (above_ground_dist_m >= edge_x0) & (above_ground_dist_m <= edge_x1)]


# take the point that is in the middle of the top_fst_bin

middle_kd_start = np.median(above_ground_ph_top_fst_bin)
middle_kd_start_dist = np.median(above_ground_dist_m[(above_ground_ph >= edge_y0) & (above_ground_ph < edge_y1) & (above_ground_dist_m >= edge_x0) & (above_ground_dist_m <= edge_x1)])


from scipy.spatial import cKDTree

tree = cKDTree(np.c_[above_ground_dist_m, above_ground_ph])

distances, indices = tree.query([[middle_kd_start_dist, middle_kd_start]], k=15)



canopy_flag = above_ground_ph[indices]
canopy_flag_dist = above_ground_dist_m[indices]

canopy_flag = np.array([])
canopy_flag_dist = np.array([])

for i in range(len(ret.statistic)):

    bin = ret.statistic[i, :]


    indices_above_mean = np.where(bin > np.nanmean(bin[bin != 0]))[0]

    # Check if there are any elements above the mean
    if len(indices_above_mean) == 0:
        # If no bin has a value above the mean, continue to the next iteration
        continue

    top_bin = indices_above_mean[-1]

    edge_y0 = biny[top_bin]
    edge_y1 = biny[top_bin + 1]
    edge_x0 = binx[i]
    edge_x1 = binx[i + 1]
    above_ground_ph_top_bin = above_ground_ph[(above_ground_ph >= edge_y0) & (above_ground_ph < edge_y1) & (above_ground_dist_m >= edge_x0) & (above_ground_dist_m <= edge_x1)]
    middle_kd_start = np.median(above_ground_ph_top_bin)
    middle_kd_start_dist = np.median(above_ground_dist_m[(above_ground_ph >= edge_y0) & (above_ground_ph < edge_y1) & (above_ground_dist_m >= edge_x0) & (above_ground_dist_m <= edge_x1)])
    tree = cKDTree(np.c_[above_ground_dist_m, above_ground_ph])
    distances, indices = tree.query([[middle_kd_start_dist, middle_kd_start]], k=15)

    # if last element of distances is larger than 1.5 times the median of the distances, then it is not a tree
    if np.any(distances > 20):
        
        continue
    else:
       
        canopy_flag = np.append(canopy_flag, above_ground_ph[indices])
        canopy_flag_dist = np.append(canopy_flag_dist, above_ground_dist_m[indices])
        continue

# Clear Jupyter Notebook cell output
clear_output_notebook()


# Plot the canopy_flag
plt.figure(figsize=(15, 5))
plt.plot(above_ground_dist_m, above_ground_ph, '.', color='green', markersize=1)
plt.plot(canopy_flag_dist, canopy_flag, '.', color='red', markersize=1)
plt.xlabel('dist [m]')
plt.ylabel('photon_h')
plt.ylim(above_ground_ph.min() -10, above_ground_ph.max() + 10)
plt.grid()
plt.show()


with open('variables.json', 'r') as json_file:
    variables = json.load(json_file)

variables['canopy_flag'] = canopy_flag.tolist()
variables['canopy_flag_dist'] = canopy_flag_dist.tolist()

variables['above_ground_dist_m'] = above_ground_dist_m.tolist()
variables['above_ground_ph'] = above_ground_ph.tolist()

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)



