from pathlib import Path
import os
from hashlib import md5
import zipfile
import logging
from logger import configure_logging

GTFS_FOLDER = 'cleaned_undefined_zombies'

data_dir_path = Path('../../data/gtfs')
in_dir_path = data_dir_path / GTFS_FOLDER
gtfs_paths = [filepath for filepath in in_dir_path.glob('*.zip')]

log_name = os.path.basename(__file__).rsplit('.', 1)[0]
configure_logging(log_path=Path('./'), log_name=log_name)
logger = logging.getLogger(log_name)

unique = []
filenames = []
for filename in gtfs_paths:
    with zipfile.ZipFile(filename, 'r') as myzip:
        contents = ''
        for name in sorted(myzip.namelist()):
            with myzip.open(name) as myfile:
                contents += myfile.read()
        filehash = md5(contents).hexdigest()
    if filehash not in unique:
        unique.append(filehash)
        filenames.append(filename)
    else:
        index = unique.index(filehash)
        logger.info(f'{filename} is duplicate of')
        logger.info(f'{filenames[index]}')
        logger.info(f'Deleting {filename}')
        os.remove(filename)
        logger.info(f'Deletion complete')
