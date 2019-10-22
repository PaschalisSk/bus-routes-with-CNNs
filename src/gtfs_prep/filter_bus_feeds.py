# Remove all non-bus routes, output may contain empty zips if no route is bus
# route

from pathlib import Path
import partridge as ptg
import logging
from BusGAN.project.utils import configure_logging
import os

INPUT_GTFS_FOLDER_NAME = 'raw'
OUTPUT_GTFS_FOLDER_NAME = 'filtered_bus_feeds'

data_dir_path = Path('../../data/gtfs')
in_dir_path = data_dir_path / INPUT_GTFS_FOLDER_NAME

out_dir_path = data_dir_path / OUTPUT_GTFS_FOLDER_NAME
out_dir_path.mkdir(parents=True, exist_ok=True)

log_name = os.path.basename(__file__).rsplit('.', 1)[0]
configure_logging(data_dir_path, log_name)
logger = logging.getLogger(log_name)

view = {
    'routes.txt': {'route_type': 3}
}
config = ptg.config.default_config()
# MUST NOT PRUNE STOPS IN ORDER NOT TO PRUNE PARENT STATIONS
# https://github.com/remix/partridge/issues/20
config.remove_edges_from(list(config.out_edges('stops.txt')))

total_gtfs_files = sum(1 for _ in in_dir_path.glob('*.zip'))
counter = 0
successful = 0

filtered_GTFS_data = [gtfs_filepath.name
                      for gtfs_filepath in out_dir_path.glob('*.zip')]
prev_filtered = len(filtered_GTFS_data)

for gtfs_filepath in in_dir_path.glob('*.zip'):
    counter = counter + 1
    gtfs_name = gtfs_filepath.name
    if gtfs_name in filtered_GTFS_data:
        logger.info(f'Skipping {gtfs_name} ({counter}/{total_gtfs_files}),'
                    f' GTFS file already filtered')
        continue
    try:
        logger.info(f'Filtering {gtfs_name} ({counter}/{total_gtfs_files})')
        ptg.extract_feed(str(gtfs_filepath),
                         str(out_dir_path/gtfs_name),
                         view,
                         config)
        successful = successful + 1
        logger.info(f'Success')
    except Exception as e:
        logger.exception(f'Error occured while filtering {gtfs_name}: {e}')

logger.info(f'Filtered {successful}/{total_gtfs_files - prev_filtered}'
            f' new GTFS files')
logger.info(f'In total {prev_filtered + successful}/{total_gtfs_files}'
            f' files have been filtered')
