import icepyx as ipx
import json
from shapely.geometry import Polygon
import numpy as np
from ipyleaflet import Map, Rectangle, Polygon, WidgetControl
from IPython.display import display, HTML
import ipywidgets as widgets
import matplotlib.cm as cm
from IPython.display import clear_output

clear_output()

# -------   1   --------- Load Variables from JSON

with open('variables.json') as json_file:
    variables = json.load(json_file)

short_name = variables['short_name']
spatial_extent = variables['spatial_extent']
date_range = variables['date_range']

lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat = spatial_extent

# -------   2   --------- Calculate the center of the bounding box

center_lat = (lower_left_lat + upper_right_lat) / 2
center_lon = (lower_left_lon + upper_right_lon) / 2


# -------   3   --------- Query ICESat-2 data granules with icepyx

region_a = ipx.Query(short_name, spatial_extent, date_range)


# -------   4   --------- Process Granules information

len_granules = len(region_a.avail_granules(ids=True)[0])

# Convert len_granules to a regular Python list
len_granules_list = len_granules.tolist() if isinstance(len_granules, np.ndarray) else len_granules
# Convert len_granules to a regular Python list
len_granules_list = len_granules.tolist() if isinstance(len_granules, np.ndarray) else len_granules

time_start = np.zeros(len_granules, dtype='U50')
time_end = np.zeros(len_granules, dtype='U50')

granules_dict = {}
granules_IDs = np.zeros(len_granules, dtype='U50')
for i in range(len_granules):
    granules_IDs[i] = region_a.granules.avail[i]['producer_granule_id']
    time_start[i] = region_a.granules.avail[i]['time_start']
    time_end[i] = region_a.granules.avail[i]['time_end']
    polygon = region_a.granules.avail[i]['polygons']
    polygon_string = polygon[0][0]
    # Split the string into individual coordinate values
    coordinates = polygon_string.split()
    polygon_coordinates = [(float(coordinates[j]), float(coordinates[j + 1])) for j in range(0, len(coordinates), 2)]
    granules_dict[f"Granule_{i + 1}"] = polygon_coordinates


for i in range(len_granules):
    time_start[i] = int((time_start[i][11:13]) + (time_start[i][14:16]) + (time_start[i][17:19]))
    time_end[i] = int((time_end[i][11:13]) + (time_end[i][14:16]) + (time_end[i][17:19]))



# -------   5   --------- Generate Colors for Granules

colormap = cm.get_cmap('rainbow', len_granules)
granule_colors_rgba = [colormap(i) for i in np.arange(len_granules) / len_granules]

# Convert RGBA values to HTML color strings
granule_colors = ['#%02x%02x%02x' % (int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)) for rgba in granule_colors_rgba]

# -------   6   --------- Create a map with the bounding box and granules

m = Map(center=[center_lat, center_lon], zoom=3)

# Add a rectangle to represent the bounding box
bounding_box = Rectangle(bounds=[(lower_left_lat, lower_left_lon), (upper_right_lat, upper_right_lon)],
                         color='blue',
                         fill_opacity=0.2,
                         fill_color='blue')
m.add_layer(bounding_box)

# Store legend HTML content with added title styles and margins
legend_html = '<b style="text-align: center; font-size: 16px; margin-bottom: 10px; display: block;">Legend</b>'
legend_html += '<div style="margin-left: 10px; margin-right: 10px;"><span style="color: blue; font-weight: bold;">&#9632;</span> Bounding Box</div>'

for k, granule_color in enumerate(granule_colors):
    # Add a polygon to represent the granule
    granule_polygon = Polygon(locations=granules_dict[f"Granule_{k + 1}"],
                             color=granule_color,
                             fill_opacity=0.2,
                             fill_color=granule_color)
    m.add_layer(granule_polygon)

    # Add legend entry with margins
    legend_html += f'<div style="margin-left: 10px; margin-right: 10px;"><span style="color: {granule_color}; font-weight: bold;">&#9632;</span> Granule {k + 1}: {granules_IDs[k]} </div>'

# Create a widget for the legend with fixed height and scrollable overflow
legend_widget = widgets.HTML(
    value=f'<div style="max-height: 300px; overflow-y: auto;">{legend_html}</div>'
)

# Create a control for the legend
legend_control = WidgetControl(widget=legend_widget, position='topright')
m.add_control(legend_control)

# Display the map
display(m)

# -------   7   --------- Convert all NumPy arrays to Python lists

# Assuming granules_IDs is a NumPy array, convert it to a Python list
granules_IDs_list = granules_IDs.tolist() if isinstance(granules_IDs, np.ndarray) else granules_IDs
time_start_list = time_start.tolist() if isinstance(time_start, np.ndarray) else time_start
time_end_list = time_end.tolist() if isinstance(time_end, np.ndarray) else time_end

# -------   8   --------- Save variables to JSON

with open('variables.json', 'r') as json_file:
    variables = json.load(json_file)

variables['len_granules'] = len_granules_list
variables['granules_IDs'] = granules_IDs_list
variables['time_start'] = time_start_list
variables['time_end'] = time_end_list

with open('variables.json', 'w') as json_file:
    json.dump(variables, json_file)






