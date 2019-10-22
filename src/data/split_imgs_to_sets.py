from pathlib import Path
from math import floor
from shutil import copy2
import random

IMG_FOLDER_NAME = 'routes_256'
train_split = 0.8
val_split = 0.1

in_dir_path = Path('../../data/route_imgs_256/')

out_dir_path = Path('../../data/datasets/') / IMG_FOLDER_NAME
out_dir_path.mkdir(parents=True, exist_ok=True)

img_paths = [filepath for filepath in in_dir_path.glob('*.jpg')]
random.shuffle(img_paths)
img_len = len(img_paths)

train_dir = out_dir_path / 'train'
train_dir.mkdir(parents=True, exist_ok=True)
for img_path in img_paths[:floor(img_len * train_split)]:
    copy2(str(img_path), train_dir)

val_dir = out_dir_path / 'val'
val_dir.mkdir(parents=True, exist_ok=True)
for img_path in img_paths[floor(img_len * train_split):floor(img_len * (train_split+val_split))]:
    copy2(str(img_path), val_dir)

test_dir = out_dir_path / 'test'
test_dir.mkdir(parents=True, exist_ok=True)
for img_path in img_paths[floor(img_len * (train_split+val_split)):]:
    copy2(str(img_path), test_dir)
