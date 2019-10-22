from pathlib import Path
import cv2

from utils.make_dataset import format_image
# id exp13 best
from models import unet_upsampling
from utils import data_utils
import os
from keras.optimizers import Adam
from scipy.misc import toimage
import keras.backend as K
from pprint import pprint
import pandas as pd
from utils.data_utils import normalization, inverse_normalization, inverse_binarization, binarization
import numpy as np
from pathlib import Path

dset = 'routes_256'
base_dir = '../../'
pretrained_weights = os.path.join(base_dir, 'experiments/unet/exp13/models/weights.best.hdf5')
nb_filters = 32
nb_conv = 4
kernel_size = (3, 3)
strides = (1, 1)
kernel_init = "he_normal"
kernel_init_mean = None
kernel_init_stddev = None
padding = "same"
up_conv_drop_layers = None
leaky_relu = None
pool_size = (2, 2)

img_dim = (256, 256, 3)

threshold = 0.15
unet_upsampling_model = unet_upsampling(img_dim, nb_filters, nb_conv,
                                        kernel_size, strides,
                                        kernel_init, kernel_init_mean,
                                        kernel_init_stddev, padding,
                                        up_conv_drop_layers, leaky_relu,
                                        pool_size)

optimizer = Adam()
unet_upsampling_model.compile(loss='binary_crossentropy',
                              optimizer=optimizer)

unet_upsampling_model.load_weights(pretrained_weights)

dset_dir = '../../data/datasets/routes_256/test/'
out_dir = '../../output/mask imgs/'

img_paths = [filepath for filepath in Path(dset_dir).glob('*.jpg')]

for img_path in img_paths:
    img_name = img_path.name
    img_path = str(img_path)
    y_img, x_img = format_image(img_path, 256, 3)
    x_img = x_img.transpose(0, 2, 3, 1)
    y_img = y_img.transpose(0, 2, 3, 1)
    x_test = normalization(x_img)
    y_test = binarization(y_img)
    y_pred = unet_upsampling_model.predict(x_test)

    x = inverse_normalization(x_test)
    y = inverse_binarization(y_test)
    y_p = inverse_binarization(y_pred, threshold=threshold)

    X = np.concatenate((np.squeeze(x), np.squeeze(y), np.squeeze(y_p)), axis=1)
    img = toimage(X)
    img.save(out_dir + img_name.rsplit('.')[0] + '.png')
    print(img_name)

print('deb')

