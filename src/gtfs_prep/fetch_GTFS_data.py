# Fetch all available GTFS feeds (the actual feed, the zips) from transitfeeds
# The file we use to get the links is produced from fetch_GTFS_links

from pathlib import Path
import requests
from BusGAN.project.utils import configure_logging
import logging
import json

data_dir_path = Path('../../data/gtfs')
out_path = data_dir_path/'raw'
out_path.mkdir(parents=True, exist_ok=True)

configure_logging(data_dir_path, 'fetch.GTFS.data')
logger = logging.getLogger('fetch.GTFS.data')

feeds_url = 'https://api.transitfeeds.com/v1/getLatestFeedVersion'
feeds_key = 'a4a1bc28-7dd3-4698-8b06-a18c97578ff6'

with open(data_dir_path / 'feeds.json') as in_file:
    feeds = json.load(in_file)

for i, feed in enumerate(feeds):
    params = {
        'key': feeds_key,
        'feed': feed['id']
    }
    name = feed['l']['t'].replace('/', ',') + ' - '\
           + feed['id'].replace('/', '-')
    out_file = out_path / f'{name}.zip'
    if out_file.is_file():
        logger.info(f'File exists.'
                    f' Skipping GTFS for {name} ({i+1}/{len(feeds)})')
        continue

    logger.info(f'Downloading GTFS for {name} ({i+1}/{len(feeds)})')

    try:
        gtfs_req = requests.get(feeds_url, params, timeout=2)
        gtfs_req.raise_for_status()
    except Exception as e:
        logger.exception(f'Error occurred while downloading {name}: {e}')
    else:
        try:
            with open(out_file, 'wb') as zip_file:
                zip_file.write(gtfs_req.content)
        except Exception as e:
            logger.exception(f'Error occurred while saving {name}: {e}')
