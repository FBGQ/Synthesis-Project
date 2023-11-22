import icepyx as ipx
import json


# User selects which data to download

with open('variables.json') as json_file:
    variables = json.load(json_file)

len_granules = variables['len_granules']
granules_IDs = variables['granules_IDs']

print('The following granules are available for download:', flush=True)
for i in range(len_granules):
    print("Granule", granules_IDs[i])

# loop the input until the user selects a valid granule
# user insert a number between 1 and len_granules
# if press escape, exit the program

i = 0

while (i < 11):
    granule_number = int(input('Select a granule to download (1 to ' + str(len_granules) + '): '))
    if granule_number < 1 or granule_number > len_granules:
        print('Invalid granule number. Please try again.', flush=True)
        i = i + 1
        if i > 10:
            print('Too many invalid inputs. Exiting...', flush=True)


Gran_ID = granules_IDs[granule_number - 1]








        
