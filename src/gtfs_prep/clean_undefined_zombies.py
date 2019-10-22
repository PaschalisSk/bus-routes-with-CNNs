# 2nd round of cleaning the GTFS data
# now we are solving the problems in
# filtered.gtfs.problems.csv.

from pathlib import Path
import os
import pandas as pd
import gtfstk
import shutil
import logging
from BusGAN.project.utils import configure_logging

# Can't really use the problems file here since some of the zombies we want
# to drop are not reported by the current validator, e.g. shapes with no trips
# or services with no trips. So we have to run this in the entire db.
#PROBLEMS_FILE = 'cleaned_feeds_custom.gtfs.problems.full.csv'
INPUT_GTFS_FOLDER_NAME = 'cleaned_feeds_custom'
OUTPUT_GTFS_FOLDER_NAME = 'cleaned_undefined_zombies'

data_dir_path = Path('../../data/gtfs')
in_dir_path = data_dir_path / INPUT_GTFS_FOLDER_NAME

out_dir_path = data_dir_path / OUTPUT_GTFS_FOLDER_NAME
out_dir_path.mkdir(parents=True, exist_ok=True)

log_name = os.path.basename(__file__).rsplit('.', 1)[0]
configure_logging(log_path=data_dir_path, log_name=log_name)
logger = logging.getLogger(log_name)

total_gtfs_files = sum(1 for _ in in_dir_path.glob('*.zip'))
cur_counter = 0

for gtfs_file_path in in_dir_path.glob('*.zip'):
    cur_counter = cur_counter + 1
    gtfs_name = gtfs_file_path.name
    logger.info(f'Cleaning {gtfs_name} ({cur_counter}/{total_gtfs_files})')
    try:
        feed = gtfstk.feed.read_gtfs(gtfs_file_path, dist_units='m')
        feed = gtfstk.cleaners.drop_undefined(feed)
        feed = gtfstk.cleaners.drop_zombies(feed)
        gtfstk.feed.write_gtfs(feed, out_dir_path / gtfs_name)
        logger.info(f'Completed')
    except Exception as e:
        logger.exception(f'Exception while cleaning {gtfs_name}: {e}')
