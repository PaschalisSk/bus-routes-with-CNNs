# Save all available GTFS feeds from transitfeeds to a file
# We are not saving the actual data but the feeds objects which have links
# for the actual data. We are downloading them using fetch_GTFS_data

from pathlib import Path
import requests
from BusGAN.project.utils import configure_logging
import logging
import json

out_path = Path('../../data/gtfs')
out_path.mkdir(parents=True, exist_ok=True)

configure_logging(out_path, 'fetch.GTFS.links')
logger = logging.getLogger('fetch.GTFS.links')

feeds_url = 'https://api.transitfeeds.com/v1/getFeeds'
feeds_key = 'a4a1bc28-7dd3-4698-8b06-a18c97578ff6'
feeds_page = 1
total_pages = None
feeds = []

while True:
    params = {
        'key': feeds_key,
        'limit': 100,
        'type': 'gtfs',
        'page': feeds_page
    }

    try:
        feeds_req = requests.get(feeds_url, params)
        feeds_req.raise_for_status()
    except Exception as e:
        logger.exception(f'Error occurred: {e}')
    else:
        json_response = feeds_req.json()
        feeds.extend(json_response['results']['feeds'])
        if total_pages is None:
            total_pages = json_response['results']['numPages']
        logger.info(f'Downloaded page {feeds_page}/{total_pages}')

    if feeds_page == total_pages:
        break
    else:
        feeds_page = feeds_page + 1

with open(out_path / 'feeds.json', 'w') as out_file:
    json.dump(feeds, out_file)
