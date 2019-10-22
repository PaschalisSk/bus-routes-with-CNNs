from pathlib import Path
import pandas as pd
base_dir = Path('../../')
imgs_path = base_dir / 'data/datasets/routes_256/test'

base_dir = '../../'
gtfs_dir = base_dir + 'data/gtfs/cleaned_undefined_zombies/'
imgs_info = pd.read_csv(base_dir + 'data/route_imgs_256/imgs_info.csv')

#for img in imgs_path.glob('*.jpg'):
img = '2.jpg'
img_info = imgs_info.loc[imgs_info['img'] == img].squeeze()
route_id = img_info['route_id']
gtfs = img_info['gtfs']
