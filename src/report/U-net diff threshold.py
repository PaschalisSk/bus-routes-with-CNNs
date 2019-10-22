# id exp13 best
from models import unet_upsampling
from utils import data_utils
import os
from keras.optimizers import Adam
from scipy.misc import toimage
import keras.backend as K
from pprint import pprint
import pandas as pd
from utils.data_utils import inverse_normalization, inverse_binarization

def plot(x, y, y_pred, threshold, figures_dir, img_pairs=3):
    x = inverse_normalization(x)
    y = inverse_binarization(y)
    y_pred = inverse_binarization(y_pred, threshold=threshold)

    # Either show img_pairs number of pairs or the max available
    img_pairs = min(img_pairs, x.shape[0])

    x = x[:img_pairs]
    y = y[:img_pairs]
    y_pred = y_pred[:img_pairs]

    X = np.concatenate((x, y, y_pred), axis=0)
    list_rows = []
    for i in range(int(X.shape[0] // img_pairs)):
        Xr = np.concatenate([X[k] for k in range(img_pairs * i,
                                                 img_pairs * (i + 1))],
                            axis=1)
        list_rows.append(Xr)

    img_matrix = np.concatenate(list_rows, axis=0)
    img = toimage(img_matrix)
    img.save(figures_dir + 'threshold_' + str(threshold) + '.png')

def binary_accuracy_threshold(threshold=0.5):
    def binary_accuracy(y_true, y_pred):
        threshold_value = threshold
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold_value), K.floatx())
        return K.mean(K.equal(y_true, K.round(y_pred)), axis=-1)

    return binary_accuracy


# https://stackoverflow.com/questions/42606207/keras-custom-decision-threshold-for-precision-and-recall
def precision_threshold(threshold=0.5):
    def precision(y_true, y_pred):
        """Precision metric.
        Computes the precision over the whole batch using threshold_value.
        """
        threshold_value = threshold
        # Adaptation of the "round()" used before to get the predictions. Clipping to make sure that the predicted raw values are between 0 and 1.
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold_value), K.floatx())
        # Compute the number of true positives. Rounding in prevention to make sure we have an integer.
        true_positives = K.round(K.sum(K.clip(y_true * y_pred, 0, 1)))
        # count the predicted positives
        predicted_positives = K.sum(y_pred)
        # Get the precision ratio
        precision_ratio = true_positives / (predicted_positives + K.epsilon())
        return precision_ratio
    return precision


def recall_threshold(threshold = 0.5):
    def recall(y_true, y_pred):
        """Recall metric.
        Computes the recall over the whole batch using threshold_value.
        """
        threshold_value = threshold
        # Adaptation of the "round()" used before to get the predictions. Clipping to make sure that the predicted raw values are between 0 and 1.
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold_value), K.floatx())
        # Compute the number of true positives. Rounding in prevention to make sure we have an integer.
        true_positives = K.round(K.sum(K.clip(y_true * y_pred, 0, 1)))
        # Compute the number of positive targets.
        possible_positives = K.sum(K.clip(y_true, 0, 1))
        recall_ratio = true_positives / (possible_positives + K.epsilon())
        return recall_ratio
    return recall

import numpy as np

out_dir = '../../output/unet thresholds/'
out_dir_imgs = out_dir + 'imgs/'
out_metrics_file = out_dir + 'metrics.csv'

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

metrics_df = pd.DataFrame(columns=['threshold, binary_accuracy',
                                   'precision', 'recall', 'f1'])

for threshold in np.arange(0.5, 0.00, -0.01):
    threshold = np.around([threshold], decimals=2)[0]
    unet_upsampling_model = unet_upsampling(img_dim, nb_filters, nb_conv,
                                            kernel_size, strides,
                                            kernel_init, kernel_init_mean,
                                            kernel_init_stddev, padding,
                                            up_conv_drop_layers, leaky_relu,
                                            pool_size)

    optimizer = Adam()
    unet_upsampling_model.compile(loss='binary_crossentropy',
                                  optimizer=optimizer,
                                  metrics=[binary_accuracy_threshold(threshold),
                                           precision_threshold(threshold),
                                           recall_threshold(threshold)])

    unet_upsampling_model.load_weights(pretrained_weights)
    test_metrics = unet_upsampling_model.evaluate(x_val, y_val, verbose=0)
    metrics_dict = dict(zip(unet_upsampling_model.metrics_names, test_metrics))
    metrics_dict['threshold'] = threshold
    if metrics_dict['precision']+metrics_dict['recall'] == 0:
        metrics_dict['f1'] = 0
    else:
        metrics_dict['f1'] = 2*(metrics_dict['precision']*metrics_dict['recall'])/(metrics_dict['precision']+metrics_dict['recall'])
    metrics_dict.pop('loss', None)
    metrics_df = metrics_df.append(pd.DataFrame(metrics_dict, index=[0]), ignore_index=True)
    pprint(metrics_dict)
    y_pred = unet_upsampling_model.predict(x_val)

    # plot(x_val[:6], y_val[:6], y_pred[:6], threshold, out_dir_imgs, img_pairs=6)

    K.clear_session()
    del unet_upsampling_model

metrics_df.to_csv(out_metrics_file, index=False)
