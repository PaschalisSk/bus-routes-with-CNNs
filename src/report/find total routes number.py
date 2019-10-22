from pathlib import Path
import gtfstk
import pandas as pd
import zipfile

GTFS_FOLDER = 'cleaned_undefined_zombies'
data_dir_path = Path('../../data/gtfs')
in_dir_path = data_dir_path / GTFS_FOLDER
gtfs_paths = [filepath for filepath in in_dir_path.glob('*.zip')]

tot_routes = 0
cur = 1
for filename in gtfs_paths:
    with zipfile.ZipFile(filename, 'r') as myzip:
        with myzip.open('routes.txt') as myfile:
            print(cur)
            cur += 1
            tot_routes += (sum(1 for line in myfile) - 1)
            print(tot_routes)
