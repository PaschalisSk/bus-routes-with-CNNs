import pandas as pd
import partridge as ptg
import math

# https://gist.github.com/rochacbruno/2883505
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 * 1000# km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

base_dir = '../../'
gtfs_dir = base_dir + 'data/gtfs/cleaned_undefined_zombies/'
imgs_info = pd.read_csv(base_dir + 'data/route_imgs_256/imgs_info.csv')
imgs_info = imgs_info.loc[imgs_info['img'].isin(['467.jpg','468.jpg','469.jpg','470.jpg'])]

final_df = pd.DataFrame(columns=['img', 'stops'])#  'stops', 'total_shape_dist',
total_rows = imgs_info.shape[0]
for index, row in imgs_info.iterrows():
    try:
        img_name = row['img']
        route_id = row['route_id']
        gtfs = row['gtfs']
        feed_query = {'routes.txt': {'route_id': route_id}}
        feed = ptg.load_feed(gtfs_dir + gtfs, view=feed_query)

        stops = feed.stops.shape[0]
        print(f'{index}/{total_rows}, {img_name}, {route_id}, {gtfs}, {stops}')
        #
        # shapes_df = feed.shapes.sort_values(["shape_id", "shape_pt_sequence"]).round(6)
        # grouped_shapes = shapes_df.groupby('shape_id')
        # # If gps pair exists then no need to readd it
        # shapes_dict = dict()
        # for shape_id, group in grouped_shapes:
        #     lat_lon_pairs = list(zip(group['shape_pt_lat'], group['shape_pt_lon']))
        #     shape_pairs = list(zip(lat_lon_pairs[:-1], lat_lon_pairs[1:]))
        #     for shape_pair in shape_pairs:
        #         if shape_pair not in shapes_dict and shape_pair[::-1] not in shapes_dict:
        #             dist = distance(*shape_pair)
        #             shapes_dict[shape_pair] = dist
        # total_shape_dist = sum(shapes_dict.values())

        # merged = pd.merge(feed.stop_times, feed.stops, on=['stop_id'])
        # merged = merged.sort_values(["trip_id", "stop_sequence"])
        # stop_dists = []
        # for trip_id, group in merged.groupby('trip_id'):
        #     lat_lon_pairs = list(zip(group['stop_lat'], group['stop_lon']))
        #     bus_stop_pairs = list(zip(lat_lon_pairs[:-1], lat_lon_pairs[1:]))
        #     for bus_stop_pair in bus_stop_pairs:
        #             dist = distance(*bus_stop_pair)
        #             stop_dists.append(dist)
        #
        # avg_stop_dist = sum(stop_dists) / (feed.stop_times.shape[0] -
        #                                    feed.stop_times['trip_id'].unique().shape[0])

        data = {'img': img_name,
                'stops': stops
                }#,
                # 'total_shape_dist': total_shape_dist,
                #'avg_stop_distance': avg_stop_dist}
        final_df = final_df.append(data, ignore_index=True)
    except:
        print('Exception')

final_df.to_csv('../../output/routes_data_analysis/stops_nb_info.csv', index=False)
