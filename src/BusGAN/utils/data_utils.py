import numpy as np
import h5py
from PIL import Image
import os


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


def load_data(dset, base_dir, reverse_dset):
    dset_file = dset + '_data.h5'
    dset_path = os.path.join(base_dir, 'data/datasets_h5/', dset_file)

    with h5py.File(dset_path, "r") as hf:

        X_full_train = hf["train_data_full"][:].astype(np.float32)
        X_full_train = normalization(X_full_train)

        X_sketch_train = hf["train_data_sketch"][:].astype(np.float32)
        X_sketch_train = normalization(X_sketch_train)

        # Move channels last
        X_full_train = X_full_train.transpose(0, 2, 3, 1)
        X_sketch_train = X_sketch_train.transpose(0, 2, 3, 1)

        X_full_val = hf["val_data_full"][:].astype(np.float32)
        X_full_val = normalization(X_full_val)

        X_sketch_val = hf["val_data_sketch"][:].astype(np.float32)
        X_sketch_val = normalization(X_sketch_val)

        X_full_val = X_full_val.transpose(0, 2, 3, 1)
        X_sketch_val = X_sketch_val.transpose(0, 2, 3, 1)

        if reverse_dset == 1:
            return X_sketch_train, X_full_train, X_sketch_val, X_full_val
        else:
            return X_full_train, X_sketch_train, X_full_val, X_sketch_val


def gen_batch(X1, X2, batch_size):
    for i in range(X1.shape[0] // batch_size):
        idx = np.arange(i * batch_size, (i + 1) * batch_size)
        yield X1[idx], X2[idx]


def get_disc_batch(X_full_batch, X_sketch_batch, generator_model,
                   batch_counter):

    # Create X_disc: alternatively only generated or real images
    if batch_counter % 2 == 0:
        # Produce an output
        X_disc = generator_model.predict(X_sketch_batch)
        # 0 for fake, 1 for real images
        y_disc = np.zeros((X_disc.shape[0], 1), dtype=np.uint8)
    else:
        X_disc = X_full_batch
        y_disc = np.ones((X_disc.shape[0], 1), dtype=np.uint8)

    return X_disc, y_disc


def plot_generated_batch(X_full, X_sketch, generator_model, batch_set,
                         figures_dir, epoch, img_pairs=3):
    # Generate images
    X_gen = generator_model.predict(X_sketch)

    X_sketch = inverse_normalization(X_sketch)
    X_full = inverse_normalization(X_full)
    X_gen = inverse_normalization(X_gen)

    img_pairs = min(img_pairs, X_sketch.shape[0])

    Xs = X_sketch[:img_pairs]
    Xg = X_gen[:img_pairs]
    Xr = X_full[:img_pairs]

    X = np.concatenate((Xs, Xg, Xr), axis=0)
    list_rows = []
    for i in range(int(X.shape[0] // img_pairs)):
        Xr = np.concatenate([X[k] for k in range(img_pairs * i,
                                                 img_pairs * (i + 1))],
                            axis=1)
        list_rows.append(Xr)

    Xr = np.concatenate(list_rows, axis=0)
    im = Image.fromarray(Xr)
    im.save(os.path.join(figures_dir, "epoch_%d_%s.png" % (epoch, batch_set)))
