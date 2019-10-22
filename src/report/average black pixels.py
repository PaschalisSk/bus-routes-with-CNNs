from utils import data_utils
from skimage.color import rgb2gray
import numpy as np

dset = 'routes_256'
base_dir = '../../'
#x_train, y_train, x_val, y_val,
x_train, y_train, x_val, y_val, x_test, y_test = data_utils.load_data(dset, base_dir)

u_train, c_train = np.unique(y_train, return_counts=True)
u_val, c_val = np.unique(y_val, return_counts=True)
u_test, c_test = np.unique(y_test, return_counts=True)
avg = (c_train[1] + c_val[1] + c_test[1])/(c_train[0] + c_train[1] + c_val[0] + c_val[1] + c_test[0] + c_test[1])
# avg = 0.016130250476253286
print(avg)
# for set in [y_train, y_val, y_test]:
#     for image in set:
#         mask_image = rgb2gray(mask_image)
#         mask_image[mask_image <= 0.5] = 0
#         mask_image[mask_image > 0.5] = 1
