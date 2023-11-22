import icepyx as ipx
import json
import matplotlib.pyplot as plt
import folium
from shapely.geometry import Polygon
import numpy as np
import geopandas as gpd
from IPython.display import IFrame
from ipyleaflet import Map, Rectangle, Polygon, WidgetControl
from IPython.display import display, HTML
import ipywidgets as widgets
import matplotlib.cm as cm

with open('variables.json') as json_file:
    variables = json.load(json_file)

short_name = variables['short_name']
spatial_extent = variables['spatial_extent']
date_range = variables['date_range']

lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat = spatial_extent
# Calculate the center of the bounding box
center_lat = (lower_left_lat + upper_right_lat) / 2
center_lon = (lower_left_lon + upper_right_lon) / 2

region_a = ipx.Query(short_name, spatial_extent, date_range)

len_granules = len(region_a.avail_granules(ids=True)[0])

granules_dict = {}
for i in range(len_granules):
    polygon = region_a.granules.avail[i]['polygons']
    polygon_string = polygon[0][0]
    # Split the string into individual coordinate values
    coordinates = polygon_string.split()
    polygon_coordinates = [(float(coordinates[j]), float(coordinates[j + 1])) for j in range(0, len(coordinates), 2)]
    granules_dict[f"Granule_{i + 1}"] = polygon_coordinates







# Generate colors using the 'viridis' colormap
colormap = cm.get_cmap('rainbow', len_granules)
granule_colors_rgba = [colormap(i) for i in np.arange(len_granules) / len_granules]

# Convert RGBA values to HTML color strings
granule_colors = ['#%02x%02x%02x' % (int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)) for rgba in granule_colors_rgba]

# Create a map centered around the bounding box
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
    legend_html += f'<div style="margin-left: 10px; margin-right: 10px;"><span style="color: {granule_color}; font-weight: bold;">&#9632;</span> Granule {k + 1}</div>'

# Create a widget for the legend
legend_widget = widgets.HTML(value=legend_html)

# Create a control for the legend
legend_control = WidgetControl(widget=legend_widget, position='topright')
m.add_control(legend_control)

# Display the map
display(m)






