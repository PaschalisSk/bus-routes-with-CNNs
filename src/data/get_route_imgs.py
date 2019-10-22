from pathlib import Path
import os

import gtfstk
import staticmap as sm
import logging
from logger import configure_logging
from PIL import Image
import pandas as pd

OUTPUT_IMG_FOLDER_NAME = 'custom'
IMG_WIDTH = 1024
IMG_HEIGHT = IMG_WIDTH
ZOOM = 15
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
saved_routes_counter = 0

# Dataframe to hold all routes we produce for each file and then write them
# to a file
routes_df = pd.DataFrame(columns=['img', 'gtfs', 'route_id',
                                  'center_lon', 'center_lat', 'zoom'])
routes_df_filepath = out_dir_path / 'imgs_info.csv'
routes_df_csv_created = False

for gtfs_file_path in in_dir_path.glob('*.zip'):
    files_counter = files_counter + 1
    gtfs_name = gtfs_file_path.name
    logger.info(f'Processing {gtfs_name} ({files_counter}/{total_files})')
    f = gtfstk.feed.read_gtfs(gtfs_file_path, dist_units='m')
    if f.shapes is not None and f.routes is not None:
        route_ids = f.routes['route_id'].unique()
        for route_id in route_ids:
            route_shape_ids = f.trips.loc[lambda x: x["route_id"] == route_id, "shape_id"].unique()
            total_route_shapes = len(route_shape_ids)
            # Check if we have more than 1 trips in that route
            # To get more "circles" i.e. back and forth trips
            if total_route_shapes > 1:
                # Check if the route shapes fit in our image
                shapes = f.shapes.loc[f.shapes['shape_id'].isin(route_shape_ids)]
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
                fits = all((min_lon <= lon <= max_lon and
                            min_lat <= lat <= max_lat) for lon, lat in coords)
                if fits:
                    try:
                        m = sm.StaticMap(IMG_WIDTH, IMG_HEIGHT,
                                     url_template=URL_TEMPLATE)
                        back_img = m.render(ZOOM, center)
                        grouped_shapes = shapes.groupby('shape_id')
                        for shape_id, trip_shapes in grouped_shapes:
                            if trip_shapes.shape[0] < 2:
                                #logger.info(f'Less than 2 shape rows')
                                continue
                            trip_shapes = trip_shapes.sort_values('shape_pt_sequence')
                            trip_coords = list(zip(trip_shapes['shape_pt_lon'],
                                                   trip_shapes['shape_pt_lat']))

                            m.add_line(sm.Line(trip_coords, 'black', 5))

                        route_img = m.render(ZOOM, center, False)

                        final_img = Image.new('RGB', (IMG_WIDTH * 2, IMG_HEIGHT))
                        final_img.paste(route_img, (0, 0))
                        final_img.paste(back_img, (IMG_WIDTH, 0))
                        final_img.save(out_dir_path /
                                       (str(saved_routes_counter + 1) + '.jpg'))

                        row = {
                            'img': str(saved_routes_counter + 1) + '.jpg',
                            'gtfs': gtfs_name,
                            'route_id': str(route_id),
                            'center_lon': center[0],
                            'center_lat': center[1],
                            'zoom': ZOOM
                        }
                        routes_df = routes_df.append(row, ignore_index=True)

                        saved_routes_counter = saved_routes_counter + 1
                    except Exception as e:
                        logger.exception(f'Exception while processing '
                                         f'{gtfs_name}/{route_id}: {e}')
                if not routes_df_csv_created:
                    routes_df.to_csv(routes_df_filepath, index=False)
                    routes_df_csv_created = True
                else:
                    routes_df.to_csv(routes_df_filepath, mode='a', index=False,
                                     header=False)
                    routes_df = pd.DataFrame(columns=['img', 'gtfs', 'route_id',
                                                      'center_lon', 'center_lat',
                                                      'zoom'])
    else:
        logger.info(f'No shapes file')
