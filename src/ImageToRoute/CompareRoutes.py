from pathlib import Path
import os
import pandas as pd
import peartree as pt
import gtfstk
import partridge as ptg

real_gtfs_dir = Path('../../data/gtfs/cleaned_undefined_zombies')
gen_gtfs_dir = Path('../../output/gtfs/')

imgs_info = pd.read_csv('../../data/route_imgs_256/imgs_info.csv')

#----------LOOP-----------#
# Loop for each generated gtfs since the generated are a subset of the cleaned
gen_filepath = gen_gtfs_dir / '1.zip'
# gen_filename is the filename without the extension
gen_filename = gen_filepath.stem
# Get the row with the info about the original gtfs the gen came from
img_info = imgs_info.loc[imgs_info['img'] == gen_filename + '.jpg']
real_filepath = real_gtfs_dir / img_info['gtfs'].values[0]
route_id = img_info['route_id'].values[0]

feed_query = {'routes.txt': {'route_id': route_id}}
gen_feed = ptg.load_feed(str(real_filepath), view=feed_query)

start = 7 * 60 * 60
end = 9 * 60 * 60
G = pt.load_feed_as_graph(gen_feed, start, end)

print('deb')
