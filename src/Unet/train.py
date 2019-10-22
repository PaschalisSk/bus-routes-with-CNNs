from utils import data_utils, general_utils
import models
import os
from keras.optimizers import Adam
from keras import callbacks
import keras.backend as K
import tensorflow as tf
import numpy as np

from exp import ex

# https://github.com/mkocabas/focal-loss-keras
def focal_loss(gamma=2., alpha=.25):
    def focal_loss_fixed(y_true, y_pred):
        pt_1 = tf.where(tf.equal(y_true, 1), y_pred, tf.ones_like(y_pred))
        pt_0 = tf.where(tf.equal(y_true, 0), y_pred, tf.zeros_like(y_pred))
        epsilon = K.epsilon()
        # clip to prevent NaN's and Inf's
        pt_1 = K.clip(pt_1, epsilon, 1. - epsilon)
        pt_0 = K.clip(pt_0, epsilon, 1. - epsilon)
        return -K.mean(alpha * K.pow(1. - pt_1, gamma) * K.log(pt_1)) - K.mean((1 - alpha) * K.pow(pt_0, gamma) * K.log(1. - pt_0))
    return focal_loss_fixed

def precision(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def recall(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def fbeta_score(y_true, y_pred, beta=1):
    if beta < 0:
        raise ValueError('The lowest choosable beta is zero (only precision).')

     # If there are no true positives, fix the F score at 0 like sklearn.
    if K.sum(K.round(K.clip(y_true, 0, 1))) == 0:
        return 0

    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    bb = beta ** 2
    fbeta_score = (1 + bb) * (p * r) / (bb * p + r + K.epsilon())
    return fbeta_score


def fmeasure(y_true, y_pred):
    return fbeta_score(y_true, y_pred, beta=1)


@ex.main
def train(_run, train_cnf, generator_cnf):
    batch_size = train_cnf["batch_size"]
    max_epochs = train_cnf["max_epochs"]
    patience = train_cnf["patience"]
    loss = train_cnf["loss"]
    learning_rate = train_cnf["learning_rate"]
    beta_1 = train_cnf["beta_1"]
    beta_2 = train_cnf["beta_2"]
    dset = train_cnf["dset"]
    base_dir = train_cnf["base_dir"]
    fig_save_freq = train_cnf["fig_save_freq"]
    fig_pairs = train_cnf["fig_pairs"]

    # Setup environment (logging directory etc)
    # Just creates the figures and models dirs
    experiment_name = 'unetfocal/exp' + str(_run._id)
    experiment_dir = os.path.join(base_dir, 'experiments', experiment_name)
    general_utils.setup_logging(experiment_dir)
    figures_dir = os.path.join(experiment_dir, 'figures')
    models_dir = os.path.join(experiment_dir, 'models')

    # Load data
    x_train, y_train, x_val, y_val, x_test, y_test = data_utils.load_data(dset, base_dir)
    img_dim = x_train.shape[-3:]

    unet_upsampling_model = models.unet_upsampling(img_dim=img_dim,
                                                   **generator_cnf)

    try:
        # Create optimizers
        optimizer = Adam(lr=learning_rate, beta_1=beta_1, beta_2=beta_2)

        class ImgPlotter(callbacks.Callback):
            def __init__(self, x_train, y_train, x_val, y_val, figures_dir,
                         fig_save_freq):
                super(ImgPlotter, self).__init__()
                self.data = {
                    'train': (x_train, y_train),
                    'val': (x_val, y_val),
                }
                self.figures_dir = figures_dir
                self.fig_save_freq = fig_save_freq

            def on_epoch_end(self, epoch, logs=None):
                if epoch % self.fig_save_freq == 0:
                    for batch_set in ['train', 'val']:
                        data_utils.plot_generated_batch(*self.data[batch_set],
                                                        self.model,
                                                        batch_set,
                                                        self.figures_dir,
                                                        epoch)

        train_idx = np.random.choice(x_train.shape[0], fig_pairs,
                                     replace=False)
        val_idx = np.random.choice(x_val.shape[0], fig_pairs,
                                   replace=False)

        imgplotter_cb = ImgPlotter(x_train[train_idx], y_train[train_idx],
                                   x_val[val_idx], y_val[val_idx],
                                   figures_dir, fig_save_freq)

        # Create the logging callback
        # The metrics are logged in the run's metrics and at heartbeat events
        # every 10 secs they get written to mongodb
        def metrics_log(epoch, logs):
            for metric_name, metric_value in logs.items():
                # The validation set keys have val_ prepended to the metric,
                # add train_ to the training set keys
                if 'val' not in metric_name:
                    metric_name = 'train_' + metric_name

                _run.log_scalar(metric_name, metric_value, epoch)

        metrics_log_cb = callbacks.LambdaCallback(on_epoch_end=metrics_log)

        model_filepath = os.path.join(models_dir, 'weights.best.hdf5')
        callbacks_list = [callbacks.EarlyStopping(
                            monitor='val_loss',
                            patience=patience),
                          callbacks.ModelCheckpoint(
                              filepath=model_filepath,
                              monitor='val_loss',
                              save_best_only=True,
                              save_weights_only=True),
                          imgplotter_cb,
                          metrics_log_cb]

        if loss == 'focal_loss':
            unet_upsampling_model.compile(loss='binary_crossentropy',
                                          optimizer=optimizer,
                                          metrics=['binary_accuracy',
                                                   precision,
                                                   recall,
                                                   fmeasure])
            unet_upsampling_model.fit(x_train, y_train, epochs=2,
                                      batch_size=batch_size,
                                      validation_data=(x_val, y_val),
                                      callbacks=callbacks_list,
                                      verbose=2)
            unet_upsampling_model.compile(loss=[focal_loss(alpha=.25, gamma=2)],
                                          optimizer=optimizer,
                                          metrics=['binary_accuracy',
                                                   precision,
                                                   recall,
                                                   fmeasure])
            unet_upsampling_model.fit(x_train, y_train, epochs=max_epochs,
                                      batch_size=batch_size,
                                      validation_data=(x_val, y_val),
                                      callbacks=callbacks_list,
                                      initial_epoch=2,
                                      verbose=2)

        elif loss == 'binary_crossentropy':
            unet_upsampling_model.compile(loss='binary_crossentropy',
                                          optimizer=optimizer,
                                          metrics=['binary_accuracy',
                                                   precision,
                                                   recall,
                                                   fmeasure])

            unet_upsampling_model.fit(x_train, y_train, epochs=max_epochs,
                                      batch_size=batch_size,
                                      validation_data=(x_val, y_val),
                                      callbacks=callbacks_list,
                                      verbose=2)

        # Clear GPU + RAM
        K.clear_session()
        del unet_upsampling_model
    except KeyboardInterrupt:
        pass
