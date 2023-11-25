import icepyx as ipx
import json
import sys
import os
from IPython.display import clear_output
import numpy as np

# User selects which data to download

with open('variables.json') as json_file:
    variables = json.load(json_file)

len_granules = variables['len_granules']
granules_IDs = variables['granules_IDs']
spatial_extent = variables['spatial_extent']
time_start = variables['time_start']
time_end = variables['time_end']

print('The following granules are available for download:', flush=True)
for i in range(len_granules):
    print("Granule", granules_IDs[i])

# loop the input until the user selects a valid granule
# user insert a number between 1 and len_granules
# if press escape, exit the program

i = 0
flag = 0

while (flag == 0):
    granule_number = int(input('Select a granule to download (1 to ' + str(len_granules) + '): '))
    if granule_number < 1 or granule_number > len_granules:
        print('Invalid granule number. Please try again.', flush=True)
        i = i + 1
        if i > 10:
            print('Too many invalid inputs. Exiting...', flush=True)
            sys.exit()
    else:
        flag = 1

clear_output()

Gran_ID = granules_IDs[granule_number - 1]

print('You selected granule', Gran_ID, flush=True)

short_name = Gran_ID[:5]
year = Gran_ID[6:10]
month = Gran_ID[10:12]
day = Gran_ID[12:14]
time = Gran_ID[14:20]
rgt = Gran_ID[21:25]
cycle = Gran_ID[25:27]
region = Gran_ID[27:29]
data = Gran_ID[30:33]
version = Gran_ID[34:36]

# region_a = ipx.Query(short_name, version = version, tracks = rgt, cycles = cycle, date_range = [year + '-' + month + '-' + day, year + '-' + month + '-' + day], start_time = time[:2] + ':' + time[2:4] + ':00' , spatial_extent = spatial_extent)

region_a = ipx.Query(short_name, spatial_extent, cycles = cycle, date_range = [year + '-' + month + '-' + day, year + '-' + month + '-' + day] )


print('Download the granule(s) (not selected granules will be removed after): ', region_a.avail_granules(ids=True)[0], flush=True)
print('Do you want to download?', flush=True)

flag = 0
while (flag == 0):
    download = input('y/n: ')
    if download == 'y' or download == 'Y':
        flag = 1
    elif download == 'n' or download == 'N':
        print('Exiting...', flush=True)
        sys.exit()
    else:
        print('Invalid input. Please try again.', flush=True)


if os.path.exists('download_data'):
    print('The folder download_data already exists.', flush=True)
    print('Do you want to overwrite the data?', flush=True)
    flag = 0
    while (flag == 0):
        overwrite = input('y/n: ')
        if overwrite == 'y' or overwrite == 'Y':
            flag = 1
        elif overwrite == 'n' or overwrite == 'N':
            print('Exiting...', flush=True)
            sys.exit()
        else:
            print('Invalid input. Please try again.', flush=True)
    os.system('rm -r download_data')


if not os.path.exists('download_data'):
    os.makedirs('download_data')
    print('Folder download_data created.', flush=True)

region_a.download_granules(path = 'download_data')

clear_output()

short_name = 'ATL08'

region_a = ipx.Query(short_name , spatial_extent, cycles = cycle, date_range = [year + '-' + month + '-' + day, year + '-' + month + '-' + day])

len_granules = len(region_a.avail_granules(ids=True)[0])
granules_IDs_ATL08 = np.zeros(len_granules, dtype='U50')
for i in range(len_granules):
    granules_IDs_ATL08[i] = region_a.granules.avail[i]['producer_granule_id']

region_a.download_granules(path = 'download_data')
clear_output()


Gran_ID = 'processed_' + Gran_ID

for file in os.listdir('download_data'):
    if file[16:29] == Gran_ID[16:29]:
        continue
    else:
        os.remove('download_data/' + file)
        print('Removed file', file, flush=True)

print('\n')


filenames = np.array([])

print('Files in the folder download_data:', flush=True)
for file in os.listdir('download_data'):
    filenames = np.append(filenames, file)
    print(file, flush=True)

with open('variables.json', 'r') as json_file:
    variables = json.load(json_file)

variables['filenames'] = filenames.tolist()

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)





