import pandas as pd
import partridge as ptg
import csv
import osmnx as ox
import networkx as nx
from staticmap import px_to_coords
from ast import literal_eval
import copy
import random

imgs_info = pd.read_csv('../../data/route_imgs_256/imgs_info.csv')
paths_list_path = '../../output/paths from skeletons/paths_list_coords.csv'
gtfs_db_dir = '../../data/gtfs/cleaned_undefined_zombies/'
nb_buses = 3
out_file = '../../output/paths compare/comp' + str(nb_buses) +'.csv'

paths_list = []
with open(paths_list_path, newline='') as paths:
    reader = csv.reader(paths, delimiter='\t')
    for row in reader:
        if reader.line_num != 1:
            row_dict = {
                'img': row[0],
                'stops': row[1:]
            }
            paths_list.append(row_dict)

nb_random_trips = 100
results_header = ['img', 'buses',
                  'my_route_avg', 'my_route_buses', 'my_route_duration',
                  'gtfs_route_avg', 'gtfs_route_buses', 'gtfs_route_duration',
                  'no_bus_equal_trips', 'total_trips']
with open(out_file, 'a') as f:
    f.writelines(','.join(str(j) for j in results_header))
    f.writelines('\n')

counter = 1
for path in [paths_list[166], paths_list[171], paths_list[172], paths_list[173]]:
    try:
        print(f'{counter}/{len(paths_list)}')
        counter += 1
        path_stops = [literal_eval(path_stop) for path_stop in path['stops']]
        img_info = imgs_info.loc[imgs_info['img'] == path['img'].rsplit('.')[0] + '.jpg']
        gtfs = img_info['gtfs'].values[0]
        route_id = img_info['route_id'].values[0]
        center = (img_info['center_lon'].values[0], img_info['center_lat'].values[0])
        zoom = img_info['zoom'].values[0]
        top_left_coords = px_to_coords((0, 0), 256, 256, zoom, center, tile_size=64)
        bot_right_coords = px_to_coords((256, 256), 256, 256, zoom, center, tile_size=64)
        north = top_left_coords[1]
        south = bot_right_coords[1]
        east = bot_right_coords[0]
        west = top_left_coords[0]

        road_g = ox.core.graph_from_bbox(north, south, east, west,
                                         network_type='drive')
        # We convert to undirected graph because a bus stop may have been placed in
        # a dead end.
        road_g = road_g.to_undirected()
        # We get the giant component because our graph has many components
        # so we may not be able to get from some point A to point B
        road_g = max(nx.connected_component_subgraphs(road_g), key=len)
        # Then again to directed but now all nodes are connected with directed edges
        road_g = road_g.to_directed()

        # Average walking speed 1.2m/s
        # https://journals.sagepub.com/doi/pdf/10.1177/0361198106198200104
        # Add the duration to travel each edge
        for u, v, d in road_g.edges(data=True):
            d['duration'] = d['length'] / 1.2
            d['mode'] = 'walk'

        random_trips = []
        for _ in range(nb_random_trips):
            random_trips.append(random.sample(road_g.nodes(), 2))

        my_routes_g = copy.deepcopy(road_g)
        # Add the first stop in the end of the stops
        path_stops.append(path_stops[0])
        # Add edges between stops
        for stop1, stop2 in zip(path_stops[:-1], path_stops[1:]):
            stop1_node = ox.utils.get_nearest_node(road_g, (stop1[1], stop1[0]))
            stop2_node = ox.utils.get_nearest_node(road_g, (stop2[1], stop2[0]))
            shortest_path_length = nx.dijkstra_path_length(road_g,
                                                           stop1_node, stop2_node,
                                                           weight='length')
            shortest_path_duration = shortest_path_length / 4.74
            my_routes_g.add_edge(stop1_node, stop2_node,
                                 length=shortest_path_length,
                                 duration=shortest_path_duration,
                                 mode='bus')

        my_route_total_duration = 0
        for (u, v, c) in my_routes_g.edges(data=True):
            if c['mode'] == 'bus':
                my_route_total_duration += c['duration']
        my_route_wait_time = (my_route_total_duration / nb_buses) / 2

        # Add waiting times by lifting bus stops
        for (u, v, d) in list(my_routes_g.edges(data=True)):
            if d['mode'] == 'bus':
                u_name, v_name = str(u) + '_bus', str(v) + '_bus'
                if not my_routes_g.has_node(u_name):
                    my_routes_g.add_node(u_name)
                    my_routes_g.add_edge(u, u_name,
                                         length=0,
                                         duration=my_route_wait_time,
                                         mode='hopon')
                    my_routes_g.add_edge(u_name, u,
                                         length=0,
                                         duration=0,
                                         mode='hopoff')
                if not my_routes_g.has_node(v_name):
                    my_routes_g.add_node(v_name)
                    my_routes_g.add_edge(v, v_name,
                                         length=0,
                                         duration=my_route_wait_time,
                                         mode='hopon')
                    my_routes_g.add_edge(v_name, v,
                                         length=0,
                                         duration=0,
                                         mode='hopoff')

                my_routes_g.add_edge(u_name, v_name,
                                     length=d['length'],
                                     duration=d['duration'],
                                     mode='bus')
                my_routes_g.remove_edge(u, v)

        gtfs_routes_g = copy.deepcopy(road_g)

        feed_query = {'routes.txt': {'route_id': route_id}}
        feed = ptg.load_feed(gtfs_db_dir + gtfs, view=feed_query)

        for i, trip in feed.trips.iterrows():
            trip_id = trip['trip_id']
            trip_stops = feed.stop_times.loc[feed.stop_times['trip_id'] == trip_id]
            trip_stops = trip_stops.sort_values('stop_sequence')
            trip_stops = trip_stops.merge(feed.stops, how='left', on='stop_id')
            trip_stops_coords = list(zip(trip_stops.stop_lon, trip_stops.stop_lat))
            if len(trip_stops_coords) > 1:
                # Add edges between stops
                for stop1, stop2 in zip(trip_stops_coords[:-1], trip_stops_coords[1:]):
                    stop1_node = ox.utils.get_nearest_node(road_g, (stop1[1], stop1[0]))
                    stop2_node = ox.utils.get_nearest_node(road_g, (stop2[1], stop2[0]))
                    bus_edge_exists = False
                    if gtfs_routes_g.has_edge(stop1_node, stop2_node):
                        edges_dict = gtfs_routes_g.get_edge_data(stop1_node, stop2_node, default=None)
                        for edge_dict_ in edges_dict:
                            if edges_dict[edge_dict_]['mode'] == 'bus':
                                bus_edge_exists = True

                    if not bus_edge_exists:
                        shortest_path_length = nx.dijkstra_path_length(road_g,
                                                                       stop1_node, stop2_node,
                                                                       weight='length')
                        shortest_path_duration = shortest_path_length / 4.74
                        gtfs_routes_g.add_edge(stop1_node, stop2_node,
                                               length=shortest_path_length,
                                               duration=shortest_path_duration,
                                               mode='bus')

        gtfs_route_total_duration = 0
        for (u, v, c) in gtfs_routes_g.edges(data=True):
            if c['mode'] == 'bus':
                gtfs_route_total_duration += c['duration']
        gtfs_route_wait_time = (gtfs_route_total_duration / nb_buses) / 2

        # Add waiting times by lifting bus stops
        for (u, v, d) in list(gtfs_routes_g.edges(data=True)):
            if d['mode'] == 'bus':
                u_name, v_name = str(u) + '_bus', str(v) + '_bus'
                if not gtfs_routes_g.has_node(u_name):
                    gtfs_routes_g.add_node(u_name)
                    gtfs_routes_g.add_edge(u, u_name,
                                         length=0,
                                         duration=gtfs_route_wait_time,
                                         mode='hopon')
                    gtfs_routes_g.add_edge(u_name, u,
                                         length=0,
                                         duration=0,
                                         mode='hopoff')
                if not gtfs_routes_g.has_node(v_name):
                    gtfs_routes_g.add_node(v_name)
                    gtfs_routes_g.add_edge(v, v_name,
                                         length=0,
                                         duration=gtfs_route_wait_time,
                                         mode='hopon')
                    gtfs_routes_g.add_edge(v_name, v,
                                         length=0,
                                         duration=0,
                                         mode='hopoff')

                gtfs_routes_g.add_edge(u_name, v_name,
                                     length=d['length'],
                                     duration=d['duration'],
                                     mode='bus')
                gtfs_routes_g.remove_edge(u, v)



        my_routes_durations = []
        my_routes_buses = 0
        gtfs_routes_durations = []
        gtfs_routes_buses = 0
        no_bus_equal_trips = 0
        for random_trip in random_trips:
            o = random_trip[0]
            d = random_trip[1]
            my_routes_dur, my_routes_path = nx.single_source_dijkstra(my_routes_g, o, d, weight='duration')
            my_routes_durations.append(my_routes_dur)

            my_bus_used = False
            for n1, n2 in zip(my_routes_path[:-1], my_routes_path[1:]):
                edges_dict = my_routes_g.get_edge_data(n1, n2,
                                                         default=None)
                if edges_dict is None:
                    print('deb')
                for edge_dict_ in edges_dict:
                    if edges_dict[edge_dict_]['mode'] == 'bus':
                        my_bus_used = True
            if my_bus_used:
                my_routes_buses += 1


            gtfs_routes_dur, gtfs_routes_path = nx.single_source_dijkstra(gtfs_routes_g, o, d, weight='duration')
            gtfs_routes_durations.append(gtfs_routes_dur)

            gtfs_bus_used = False
            for n1, n2 in zip(gtfs_routes_path[:-1], gtfs_routes_path[1:]):
                edges_dict = gtfs_routes_g.get_edge_data(n1, n2,
                                                         default=None)
                for edge_dict_ in edges_dict:
                    if edges_dict[edge_dict_]['mode'] == 'bus':
                        gtfs_bus_used = True
            if gtfs_bus_used:
                gtfs_routes_buses += 1

            if (not my_bus_used) and (not gtfs_bus_used):
                no_bus_equal_trips += 1

        my_routs_avg = sum(my_routes_durations) / len(my_routes_durations)
        gtfs_routes_avg = sum(gtfs_routes_durations) / len(gtfs_routes_durations)
        result_row = [path['img'], nb_buses,
                      my_routs_avg, my_routes_buses, my_route_total_duration,
                      gtfs_routes_avg, gtfs_routes_buses,  gtfs_route_total_duration,
                      no_bus_equal_trips, nb_random_trips]

        # with open(out_file, 'a') as f:
        #     f.writelines(','.join(str(j) for j in result_row))
        #     f.writelines('\n')
    except:
        print('exc')
        continue
