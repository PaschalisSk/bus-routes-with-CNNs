# Goes through the zips in filtered folder (only buses) cleans them
# using the cleaning methods of gtfstk library*. The most important thing here
# is that we filter out empty zips or zips without required tables
# * Just dropping invalid columns

from pathlib import Path
import gtfstk
import pandas as pd
import shutil
import os
import logging
from BusGAN.project.utils import configure_logging

PROBLEMS_FILE = 'filtered.gtfs.problems.csv'
INPUT_GTFS_FOLDER_NAME = 'filtered_bus_feeds'
OUTPUT_GTFS_FOLDER_NAME = 'filtered_empty_feeds_invalid_columns'

data_dir_path = Path('../../data/gtfs')
in_dir_path = data_dir_path / INPUT_GTFS_FOLDER_NAME

out_dir_path = data_dir_path / OUTPUT_GTFS_FOLDER_NAME
out_dir_path.mkdir(parents=True, exist_ok=True)

problems_dir_path = Path('../../output/gtfs problems/')
problems_df = pd.read_csv(problems_dir_path / PROBLEMS_FILE)
# Filter out the problems we don't care about
problems_df = problems_df[(problems_df['message'] !=
                           'Repeated pair (trip_id, departure_time)')
                          & (problems_df['message'] != 'Feed expired')
                          & (problems_df['message'] !=
                             'Repeated pair (route_short_name, '
                             'route_long_name)')]
# Get the names of the files with errors so that we can just copy the rest
gtfs_names_with_problems = problems_df['gtfs_name'].unique()

log_name = os.path.basename(__file__).rsplit('.', 1)[0]
configure_logging(log_path=data_dir_path, log_name=log_name)
logger = logging.getLogger(log_name)

total_gtfs_files = sum(1 for _ in in_dir_path.glob('*.zip'))
cur_counter = 0

for gtfs_file_path in in_dir_path.glob('*.zip'):
    gtfs_name = gtfs_file_path.name
    cur_counter = cur_counter + 1
    if gtfs_name in gtfs_names_with_problems:
        logger.info(f'Cleaning {gtfs_name} ({cur_counter}/{total_gtfs_files})')
        try:
            cur_problems = problems_df[problems_df['gtfs_name'] == gtfs_name]
            problem_msgs = cur_problems['message'].values
            if ('Missing table' in problem_msgs or
                    'Missing both tables' in problem_msgs):
                logger.info(f'Missing table, skipping')
                continue
            # Dist units doesn't matter as long as we use the same at the write
            # operation
            feed = gtfstk.feed.read_gtfs(gtfs_file_path, dist_units='m')
            feed = feed.drop_invalid_columns()
            gtfstk.feed.write_gtfs(feed, out_dir_path / gtfs_name)
            logger.info(f'Completed')
        except Exception as e:
            logger.exception(f'Error while cleaning file {gtfs_name}: {e}')
    else:
        logger.info(f'Copying {gtfs_name} ({cur_counter}/{total_gtfs_files})')
        try:
            shutil.copy(str(gtfs_file_path), str(out_dir_path))
            logger.info(f'Completed')
        except Exception as e:
            logger.exception(f'Exception while copying {gtfs_name}: {e}')
