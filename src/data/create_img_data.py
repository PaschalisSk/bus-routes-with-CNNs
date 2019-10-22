from pathlib import Path
import os

import gtfstk
import staticmap as sm
import logging
from logging import configure_logging
from PIL import Image
import pandas as pd

OUTPUT_IMG_FOLDER_NAME = 'custom'
IMG_WIDTH = 1024
IMG_HEIGHT = IMG_WIDTH
ZOOM = 16
URL_TEMPLATE = 'https://api.maptiler.com/maps/ac954d00-25c8-4a7a-8773-40afb4d17a18/256/{z}/{x}/{y}.jpg?key=3rAT6TUcA56m3Ge4l5Xk'

in_dir_path = Path('../../data/gtfs/cleaned_undefined_zombies')

out_data_path = Path('../../data/route_imgs/')
out_dir_path = out_data_path / OUTPUT_IMG_FOLDER_NAME
out_dir_path.mkdir(parents=True, exist_ok=True)

log_name = str(os.path.basename(__file__).rsplit('.', 1)[0])
configure_logging(log_path=out_dir_path, log_name=log_name)
logger = logging.getLogger(log_name)

total_files = sum(1 for _ in in_dir_path.glob('*.zip'))
files_counter = 0
saved_shapes_counter = 0

# Dataframe to hold all shapes we produce for each file and then write them
# to a file
shapes_df = pd.DataFrame(columns=['img', 'gtfs', 'shape_id',
                                  'center_lon', 'center_lat', 'zoom'])
shapes_df_filepath = out_dir_path / 'imgs_info.csv'
shapes_df_csv_created = False

for gtfs_file_path in in_dir_path.glob('*.zip'):
    files_counter = files_counter + 1
    gtfs_name = gtfs_file_path.name
    logger.info(f'Processing {gtfs_name} ({files_counter}/{total_files})')
    f = gtfstk.feed.read_gtfs(gtfs_file_path, dist_units='m')
    if f.shapes is not None:
        shape_ids = f.shapes['shape_id'].unique()
        total_shapes = len(shape_ids)
        shape_counter = 0
        for shape_id in shape_ids:
            shape_counter = shape_counter + 1
            #logger.info(f'Processing shape {shape_counter}/{total_shapes}')
            try:
                m = sm.StaticMap(IMG_WIDTH, IMG_HEIGHT,
                                 url_template=URL_TEMPLATE)
                shapes = f.shapes.loc[f.shapes['shape_id'] == shape_id]
                if shapes.shape[0] < 2:
                    #logger.info(f'Less than 2 shape rows')
                    continue

                shapes = shapes.sort_values('shape_pt_sequence')

                coords = list(zip(shapes['shape_pt_lon'],
                                  shapes['shape_pt_lat']))

                lon_center = (min(coords, key=lambda x: x[0])[0] +
                              max(coords, key=lambda x: x[0])[0]) / 2
                lat_center = (min(coords, key=lambda x: x[1])[1] +
                              max(coords, key=lambda x: x[1])[1]) / 2
                center = [lon_center, lat_center]

                min_lon, min_lat = sm.px_to_coords((0, IMG_HEIGHT),
                                                   IMG_WIDTH, IMG_HEIGHT,
                                                   ZOOM, center)
                max_lon, max_lat = sm.px_to_coords((IMG_WIDTH, 0),
                                                   IMG_WIDTH, IMG_HEIGHT,
                                                   ZOOM, center)
                if all((min_lon <= lon <= max_lon and
                        min_lat <= lat <= max_lat) for lon, lat in coords):
                    back_img = m.render(ZOOM, center)

                    m.add_line(sm.Line(coords, 'black', 5))
                    route_img = m.render(ZOOM, center, False)

                    final_img = Image.new('RGB', (IMG_WIDTH * 2, IMG_HEIGHT))
                    final_img.paste(route_img, (0, 0))
                    final_img.paste(back_img, (IMG_WIDTH, 0))
                    final_img.save(out_dir_path /
                                   (str(saved_shapes_counter + 1) + '.png'))

                    row = {
                        'img': str(saved_shapes_counter + 1) + '.png',
                        'gtfs': gtfs_name,
                        'shape_id': str(shape_id),
                        'center_lon': center[0],
                        'center_lat': center[1],
                        'zoom': ZOOM
                    }
                    shapes_df = shapes_df.append(row, ignore_index=True)

                    saved_shapes_counter = saved_shapes_counter + 1
                    #logger.info(f'Completed')
                else:
                    #logger.info(f'Shape out of bounds')
                    continue
            except Exception as e:
                logger.exception(f'Exception while processing '
                                 f'{gtfs_name}/{shape_id}: {e}')
        if not shapes_df_csv_created:
            shapes_df.to_csv(shapes_df_filepath, index=False)
            shapes_df_csv_created = True
        else:
            shapes_df.to_csv(shapes_df_filepath, mode='a', index=False,
                             header=False)
            shapes_df = pd.DataFrame(columns=['img', 'gtfs', 'shape_id',
                                              'center_lon', 'center_lat',
                                              'zoom'])
    else:
        logger.info(f'No shapes file')
# # lon, lat of Thessaloniki greece in order to get the lon and lat size
# # we are able to fit in one image.
# sample_center = (22.942679, 40.630828)
# sample_center = (-67.185532, 0.695716)
# sample_min_lon, sample_min_lat = sm.px_to_coords((0, IMG_HEIGHT),
#                                                  IMG_WIDTH, IMG_HEIGHT,
#                                                  ZOOM, sample_center)
# sample_max_lon, sample_max_lat = sm.px_to_coords((IMG_WIDTH, 0),
#                                                  IMG_WIDTH, IMG_HEIGHT,
#                                                  ZOOM, sample_center)
# lon_size = sample_max_lon - sample_min_lon
# lat_size = sample_max_lat - sample_min_lat
#
# f = gtfstk.read_gtfs(in_dir_path / 'Iowa City, IA, USA - cambus-1024.zip', dist_units='km')
#
#
# m = sm.StaticMap(IMG_WIDTH, IMG_HEIGHT,
#                  url_template="https://basemaps.cartocdn.com/rastertiles/"
#                               "voyager_no_labels_no_buildings/{z}/{x}/{y}.png")
#
# trip_id = 't_744399_b_16448_tn_0'
# shape_id = f.trips.loc[f.trips['trip_id'] == trip_id, 'shape_id'].tolist()[0]
# shapes = f.shapes.loc[f.shapes['shape_id'] == shape_id].sort_values(
#     'shape_pt_sequence')
#
#
#
# final_im = Image.new('RGB', (IMG_WIDTH * 2, IMG_HEIGHT))
# back_im = m.render(ZOOM, center)
#
#
# #test = 0.02
#
# m.add_line(sm.Line(coords, 'black', 3))
# m.add_marker(sm.CircleMarker(sm.px_to_coords((512, 512), IMG_WIDTH, IMG_HEIGHT, ZOOM, center), 'red', 12))
# m.add_marker(sm.CircleMarker(sm.px_to_coords((0, 0), IMG_WIDTH, IMG_HEIGHT, ZOOM, center), 'red', 12))
# m.add_marker(sm.CircleMarker(sm.px_to_coords((0, 1024), IMG_WIDTH, IMG_HEIGHT, ZOOM, center), 'green', 12))
# m.add_marker(sm.CircleMarker(sm.px_to_coords((1024, 0), IMG_WIDTH, IMG_HEIGHT, ZOOM, center), 'blue', 12))
# m.add_marker(sm.CircleMarker(sm.px_to_coords((1024, 1024), IMG_WIDTH, IMG_HEIGHT, ZOOM, center), 'yellow', 12))
#
# # lon_dif = m.px_to_coords((1024, 0))[0] - m.px_to_coords((0, 0))[0]
# # lat_dif = m.px_to_coords((0, 0))[1] - m.px_to_coords((0, 1024))[1]
#
# route_im = m.render(ZOOM, center)
#
# #final_im.save('asd.jpeg')
# final_im.show()
# print('deb')

# ---------------------- #
# my_dpi = 106
# min_lon, min_lat, max_lon, max_lat = feed.compute_bounds()
#
# default_width = 4
# default_big_width = 6
#
# bgcolor = '#000000'
# default_color = '#ffffff'
# motorway_color = '#ea90a0'
# trunk_color = '#fbb299'
# primary_color = '#fdd7a1'
# secondary_color = '#f6fabb'
# smooth_joints = True
#
# fig_width = None
# fig_height = 768
#
# use_geom = True
#
# edge_alpha = 1
# margin = 0
# axis_off = True
# equal_aspect = False
# annotate=False
#
# G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon,
#                        simplify=False, truncate_by_edge=True,
#                        network_type='drive')
# G = ox.simplify_graph(G, strict=False)
#
# # if user did not pass in custom street widths, create a dict of default
# # values
# street_widths = {'footway': 1.5,
#                  'steps': 1.5,
#                  'pedestrian': 1.5,
#                  'service': 1.5,
#                  'path': 1.5,
#                  'track': 1.5,
#                  'tertiary_link': default_big_width,
#                  'secondary_link': default_big_width,
#                  'primary_link': default_big_width,
#                  'trunk_link': default_big_width,
#                  'motorway_link': default_big_width,
#                  'tertiary': default_big_width,
#                  'secondary': default_big_width,
#                  'primary': default_big_width,
#                  'trunk': default_big_width,
#                  'motorway': default_big_width}
#
# street_colors = {'secondary_link': secondary_color,
#                  'primary_link': primary_color,
#                  'trunk_link': trunk_color,
#                  'motorway_link': motorway_color,
#                  'secondary': secondary_color,
#                  'primary': primary_color,
#                  'trunk': trunk_color,
#                  'motorway': motorway_color}
# # we need an undirected graph to find every edge incident to a node
# G_undir = G.to_undirected()
#
# # for each network edge, get a linewidth according to street type (the OSM
# # 'highway' value)
# edge_linewidths = []
# edge_colors = []
# for _, _, data in G_undir.edges(keys=False, data=True):
#     street_type = data['highway'][0] if isinstance(data['highway'], list) else \
#     data['highway']
#     if street_type in street_widths:
#         edge_linewidths.append(street_widths[street_type])
#     else:
#         edge_linewidths.append(default_width)
#
#     if street_type in street_colors:
#         edge_colors.append(street_colors[street_type])
#     else:
#         edge_colors.append(default_color)
#
#     if smooth_joints:
#         # for each node, get a nodesize according to the narrowest incident edge
#         node_widths = {}
#         for node in G_undir.nodes():
#             # first, identify all the highway types of this node's incident edges
#             incident_edges_data = [G_undir.get_edge_data(node, neighbor) for neighbor in G_undir.neighbors(node)]
#             edge_types = [data[0]['highway'] for data in incident_edges_data]
#             if len(edge_types) < 1:
#                 # if node has no incident edges, make size zero
#                 node_widths[node] = 0
#             else:
#                 # flatten the list of edge types
#                 edge_types_flat = []
#                 for et in edge_types:
#                     if isinstance(et, list):
#                         edge_types_flat.extend(et)
#                     else:
#                         edge_types_flat.append(et)
#
#                 # for each edge type in the flattened list, lookup the
#                 # corresponding width
#                 edge_widths = [street_widths[edge_type] if edge_type in street_widths else default_width for edge_type in edge_types_flat]
#
#                 # the node diameter will be the biggest of the edge widths, to make joints perfectly smooth
#                 # alternatively, use min (?) to pervent anything larger from extending past smallest street's line
#                 circle_diameter = max(edge_widths)
#
#                 # mpl circle marker sizes are in area, so it is the diameter
#                 # squared
#                 circle_area = circle_diameter ** 2
#                 node_widths[node] = circle_area
#
#         # assign the node size to each node in the graph
#         node_sizes = [node_widths[node] for node in G_undir.nodes()]
#     else:
#         node_sizes = 0
#
# bbox = (max_lat, min_lat, max_lon, min_lon)
#
# node_Xs = [float(x) for _, x in G.nodes(data='x')]
# node_Ys = [float(y) for _, y in G.nodes(data='y')]
#
# north, south, east, west = bbox
#
# # if caller did not pass in a fig_width, calculate it proportionately from
# # the fig_height and bounding box aspect ratio
# bbox_aspect_ratio = (north - south) / (east - west)
# if fig_width is None:
#     fig_width = fig_height / bbox_aspect_ratio
#
# # create the figure and axis
# fig, ax = plt.subplots(figsize=(fig_width/my_dpi, fig_height/my_dpi),
#                        facecolor=bgcolor,
#                        dpi=my_dpi)
# ax.set_facecolor(bgcolor)
#
# lines = []
# for u, v, data in G.edges(keys=False, data=True):
#     if 'geometry' in data and use_geom:
#         # if it has a geometry attribute (a list of line segments), add them
#         # to the list of lines to plot
#         xs, ys = data['geometry'].xy
#         lines.append(list(zip(xs, ys)))
#     else:
#         # if it doesn't have a geometry attribute, the edge is a straight
#         # line from node to node
#         x1 = G.nodes[u]['x']
#         y1 = G.nodes[u]['y']
#         x2 = G.nodes[v]['x']
#         y2 = G.nodes[v]['y']
#         line = [(x1, y1), (x2, y2)]
#         lines.append(line)
#
# # add the lines to the axis as a linecollection
# lc = LineCollection(lines, colors=edge_colors, linewidths=edge_linewidths, alpha=edge_alpha, zorder=2)
# ax.add_collection(lc)
#
# # scatter plot the nodes
# # ax.scatter(node_Xs, node_Ys, s=node_size, c=node_color, alpha=node_alpha,
# #            edgecolor=node_edgecolor, zorder=node_zorder)
#
# # set the extent of the figure
# margin_ns = (north - south) * margin
# margin_ew = (east - west) * margin
# ax.set_ylim((south - margin_ns, north + margin_ns))
# ax.set_xlim((west - margin_ew, east + margin_ew))
#
# # configure axis appearance
# xaxis = ax.get_xaxis()
# yaxis = ax.get_yaxis()
#
# xaxis.get_major_formatter().set_useOffset(False)
# yaxis.get_major_formatter().set_useOffset(False)
#
# # if axis_off, turn off the axis display set the margins to zero and point
# # the ticks in so there's no space around the plot
# if axis_off:
#     ax.axis('off')
#     ax.margins(0)
#     ax.tick_params(which='both', direction='in')
#     xaxis.set_visible(False)
#     yaxis.set_visible(False)
#     fig.canvas.draw()
#
# if equal_aspect:
#     # make everything square
#     ax.set_aspect('equal')
#     fig.canvas.draw()
# else:
#     # if the graph is not projected, conform the aspect ratio to not stretch the plot
#     if G.graph['crs'] == ox.settings.default_crs:
#         coslat = np.cos((min(node_Ys) + max(node_Ys)) / 2. / 180. * np.pi)
#         ax.set_aspect(1. / coslat)
#         fig.canvas.draw()
#
# # annotate the axis with node IDs if annotate=True
# if annotate:
#     for node, data in G.nodes(data=True):
#         ax.annotate(node, xy=(data['x'], data['y']))
#
# plt.show()
# fig, ax = ox.plot_figure_ground(Gdrive, dist=2500, show=True, save=False)
# trip_id = f.trips.loc[f.trips['shape_id'] == 'p_177718', 'trip_id'].tolist()

# ------------------------------------- #

# import folium as fl
# import folium.plugins as fp
# import shapely.geometry as sg
# import shapely.ops as so
#
# trip_ids = ['t_744399_b_16448_tn_0']
# include_stops = False
# color_palette = gtfstk.constants.COLORS_SET2
#
#
# # Get routes slice and convert to dictionary
# trips = (
#     feed.trips.loc[lambda x: x["trip_id"].isin(trip_ids)]
#         .fillna("n/a")
#         .to_dict(orient="records")
# )
#
# # Create colors
# n = len(trips)
# colors = [color_palette[i % len(color_palette)] for i in range(n)]
#
# # Initialize map
# my_map = fl.Map(tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png",
#                 attr='Mapbox attribution')
#
# # Collect route bounding boxes to set map zoom later
# bboxes = []
#
# # Create a feature group for each route and add it to the map
# for i, trip in enumerate(trips):
#     collection = feed.trip_to_geojson(
#         trip_id=trip["trip_id"], include_stops=include_stops
#     )
#     group = fl.FeatureGroup(name="Trip " + trip["trip_id"])
#     color = colors[i]
#
#     for f in collection["features"]:
#         prop = f["properties"]
#
#         # Add stop
#         if f["geometry"]["type"] == "Point":
#             lon, lat = f["geometry"]["coordinates"]
#             fl.CircleMarker(
#                 location=[lat, lon],
#                 radius=8,
#                 fill=True,
#                 color=color,
#                 weight=1,
#                 popup=fl.Popup(gtfstk.helpers.make_html(prop)),
#             ).add_to(group)
#
#         # Add path
#         else:
#             # Path
#             prop["color"] = color
#             path = fl.GeoJson(
#                 f,
#                 name=trip,
#                 style_function=lambda x: {
#                     "color": x["properties"]["color"]
#                 },
#             )
#             path.add_child(fl.Popup(gtfstk.helpers.make_html(prop)))
#             path.add_to(group)
#
#             # # Direction arrows, assuming, as GTFS does, that
#             # # trip direction equals LineString direction
#             # fp.PolyLineTextPath(
#             #     path,
#             #     "        \u27A4        ",
#             #     repeat=True,
#             #     offset=5.5,
#             #     attributes={"fill": color, "font-size": "18"},
#             # ).add_to(group)
#
#             bboxes.append(sg.box(*sg.shape(f["geometry"]).bounds))
#
#     group.add_to(my_map)
#
# # fl.LayerControl().add_to(my_map)
#
# # Fit map to bounds
# bounds = so.unary_union(bboxes).bounds
# bounds2 = [bounds[1::-1], bounds[3:1:-1]]  # Folium expects this ordering
# my_map.fit_bounds(bounds2)
#
#
# def save_map(map, delay=3):
#     from selenium import webdriver
#     import time
#
#     options = webdriver.firefox.options.Options()
#     options.add_argument('--headless')
#     driver = webdriver.Firefox(options=options)
#
#     html = map.get_root().render()
#     with fl.utilities._tmp_html(html) as fname:
#         # We need the tempfile to avoid JS security issues.
#         driver.get('file:///{path}'.format(path=fname))
#         driver.set_window_size(1024, 1024)
#         #driver.maximize_window()
#         time.sleep(delay)
#         png = driver.get_screenshot_as_png()
#         driver.quit()
#
#     with open('index.png', 'wb') as the_file:
#         the_file.write(png)
#
#
# save_map(my_map)
# my_map.save('index.html')

# -------------------------------- #
