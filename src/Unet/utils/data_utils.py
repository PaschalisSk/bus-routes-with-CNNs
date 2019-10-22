import numpy as np
import h5py
import os
from scipy.misc import toimage


def normalization(X):
    result = X / 127.5 - 1
    
    # Deal with the case where float multiplication
    # gives an out of range result (eg 1.000001)
    out_of_bounds_high = (result > 1.)
    out_of_bounds_low = (result < -1.)
    
    if not all(np.isclose(result[out_of_bounds_high],1)):
        raise RuntimeError("Normalization gave a value greater than 1")
    else:
        result[out_of_bounds_high] = 1.
        
    if not all(np.isclose(result[out_of_bounds_low],-1)):
        raise RuntimeError("Normalization gave a value lower than -1")
    else:
        result[out_of_bounds_low] = -1.
    
    return result


def inverse_normalization(X):
    # normalises back to ints 0-255, as more reliable than floats 0-1
    # (np.isclose is unpredictable with values very close to zero)
    result = ((X + 1.) * 127.5).astype('uint8')
    # Still check for out of bounds, just in case
    out_of_bounds_high = (result > 255)
    out_of_bounds_low = (result < 0)
    
    if out_of_bounds_high.any():
        raise RuntimeError("Inverse normalization gave a "
                           "value greater than 255")
        
    if out_of_bounds_low.any():
        raise RuntimeError("Inverse normalization gave a value lower than 1")
        
    return result


def binarization(y):
    # Turn RGB bus route target image of shape (batch_size, h, w, channels=3)
    # To B/W(mask) (batch_size, h, w, channels=1)
    # Make arr of size (batch_size, h, w)
    # TODO: could be vectorised?
    masks = np.empty(y.shape[:-1])
    for i in range(y.shape[0]):
        # Convert numpy array to RGB pillow Image
        img = toimage(y[i])
        # Convert to black and white
        img = img.convert('L')
        # Convert black and white pillow image to numpy array (wxh)
        img = np.array(img)
        # Pixels below 220(black, i.e. route) to 1, whites to 0
        img = np.where(img < 220, 1, 0)
        masks[i] = img
    # Add the channel dim
    masks = np.expand_dims(masks, axis=-1)
    return masks


def inverse_binarization(y, threshold=0.5):
    # Turn B/W(mask) of size (batch_size, h, w, channels=1)
    # To RGB bus route target image of shape (batch_size, h, w, channels=3)
    # Threshold above which probability the pixel is black
    imgs = np.where(y > threshold, 0, 255)
    imgs = np.tile(imgs, (1, 1, 1, 3))
    return imgs


def load_data(dset, base_dir, test_only=False):
    dset_file = dset + '_data.h5'
    dset_path = os.path.join(base_dir, 'data/datasets_h5/', dset_file)

    with h5py.File(dset_path, "r") as hf:

        x_test = hf["test_data_sketch"][:].astype(np.float32)
        x_test = normalization(x_test)

        y_test = hf["test_data_full"][:].astype(np.float32)

        x_test = x_test.transpose(0, 2, 3, 1)
        y_test = y_test.transpose(0, 2, 3, 1)
        y_test = binarization(y_test)

        if test_only:
            return x_test, y_test

        x_val = hf["val_data_sketch"][:].astype(np.float32)
        x_val = normalization(x_val)

        y_val = hf["val_data_full"][:].astype(np.float32)

        x_val = x_val.transpose(0, 2, 3, 1)
        y_val = y_val.transpose(0, 2, 3, 1)
        y_val = binarization(y_val)

        x_train = hf["train_data_sketch"][:].astype(np.float32)
        x_train = normalization(x_train)

        y_train = hf["train_data_full"][:].astype(np.float32)
        # Move channels last
        x_train = x_train.transpose(0, 2, 3, 1)
        y_train = y_train.transpose(0, 2, 3, 1)
        y_train = binarization(y_train)

        return x_train, y_train, x_val, y_val, x_test, y_test


def plot_generated_batch(x, y, model, batch_set,
                         figures_dir, epoch, img_pairs=3):
    # Generate images
    y_pred = model.predict(x)

    x = inverse_normalization(x)
    y = inverse_binarization(y)
    y_pred = inverse_binarization(y_pred)

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
    img.save(os.path.join(figures_dir, "epoch_%d_%s.png" % (epoch, batch_set)))


if __name__ == '__main__':
    load_data('routes_256', '../../../')
