from models import unet_upsampling
from utils import data_utils
import os
from keras.optimizers import Adam
from scipy.misc import toimage
from train import precision, recall, fmeasure
import numpy as np

out_dir = '../../output/unet thresholds/'
out_dir_imgs = '../../output/unet thresholds/imgs'
out_metrics_file = '../../output/unet thresholds/metrics.csv'

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

x_train, y_train, x_val, y_val, x_test, y_test = data_utils.load_data(dset, base_dir)

img_dim = x_test.shape[-3:]

unet_upsampling_model = unet_upsampling(img_dim, nb_filters, nb_conv,
                                        kernel_size, strides,
                                        kernel_init, kernel_init_mean,
                                        kernel_init_stddev, padding,
                                        up_conv_drop_layers, leaky_relu,
                                        pool_size)

optimizer = Adam()
unet_upsampling_model.compile(loss='binary_crossentropy',
                              optimizer=optimizer,
                              metrics=['binary_accuracy',
                                       precision,
                                       recall,
                                       fmeasure])


unet_upsampling_model.load_weights(pretrained_weights)
test_metrics = unet_upsampling_model.evaluate(x_val, y_val, verbose=0)
metrics_dict = dict(zip(unet_upsampling_model.metrics_names, test_metrics))

y_pred = unet_upsampling_model.predict(x_test)

imgs_arr = data_utils.inverse_binarization(y_pred, 0.25)
img = toimage(imgs_arr[0])
img.save('test.png')
print('deb')

