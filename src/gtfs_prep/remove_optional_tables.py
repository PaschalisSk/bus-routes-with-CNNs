from pathlib import Path
import os
import pandas as pd
import gtfstk
import shutil
import logging
import datetime
import logging
import sys
import zipfile

def configure_logging(log_path: Path, log_name: str) -> None:
    """ Configure logger

    Args:
        log_path: The output directory for the log file
        log_name: The logger name
    """
    datetime_string = datetime.datetime.now().strftime('.%Y-%m-%d--%H-%M-%S')
    log_filename = log_name + datetime_string + '.log'
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    fh = logging.FileHandler(filename=log_path / log_filename,
                             encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

INPUT_GTFS_FOLDER_NAME = 'cleaned_undefined_zombies'
OUTPUT_GTFS_FOLDER_NAME = 'removed_optional_tables'

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
        zin = zipfile.ZipFile(gtfs_file_path, 'r')
        zout = zipfile.ZipFile(out_dir_path / gtfs_name, 'w')
        for item in zin.infolist():
            buffer = zin.read(item.filename)
            if (item.filename not in ['fare_attributes.txt', 'fare_rules.txt', 'frequencies.txt', 'transfers.txt', 'pathways.txt', 'levels.txt', 'feed_info.txt']):
                zout.writestr(item, buffer)
        zout.close()
        zin.close()
        logger.info(f'Completed')
    except Exception as e:
        logger.exception(f'Exception while cleaning {gtfs_name}: {e}')



