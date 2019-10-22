from utils import data_utils, general_utils
import models

import os
import numpy as np

from keras.optimizers import Adam
import keras.backend as K

from exp import ex


def l1_loss(y_true, y_pred):
    return K.sum(K.abs(y_pred - y_true), axis=-1)


@ex.main
def train(_run, train_cnf, generator_cnf, discriminator_cnf):
    generator = train_cnf["generator"]
    discriminator = train_cnf["discriminator"]
    batch_size = train_cnf["batch_size"]
    nb_epoch = train_cnf["nb_epoch"]
    learning_rate = train_cnf["learning_rate"]
    beta_1 = train_cnf["beta_1"]
    beta_2 = train_cnf["beta_2"]
    l1_weight = train_cnf["l1_weight"]
    dset = train_cnf["dset"]
    base_dir = train_cnf["base_dir"]
    model_save_epoch = train_cnf["model_save_epoch"]
    fig_save_epoch = train_cnf["fig_save_epoch"]
    reverse_dset = train_cnf["reverse_dset"]

    # Setup environment (logging directory etc)
    # Just creates the figures and models dirs
    experiment_name = 'busgan/exp' + str(_run._id)
    experiment_dir = os.path.join(base_dir, 'experiments', experiment_name)
    general_utils.setup_logging(experiment_dir)

    # Load and rescale data
    X_full_train, X_sketch_train, X_full_val, X_sketch_val = data_utils.load_data(dset, base_dir, reverse_dset)
    img_dim = X_full_train.shape[-3:]

    if generator == 'generator_unet_upsampling':
        generator_model = models.generator_unet_upsampling(img_dim=img_dim,
                                                           **generator_cnf)
    elif generator == 'generator_upsampling':
        generator_model = models.generator_upsampling(img_dim=img_dim,
                                                      **generator_cnf)
    else:
        raise ValueError('Generator name not recognised')

    if discriminator == 'DCGAN_discriminator':
        discriminator_model = models.DCGAN_discriminator(img_dim=img_dim,
                                                         **discriminator_cnf)
    else:
        raise ValueError('Discriminator name not recognised')

    batches_per_e = X_full_train.shape[0] // batch_size

    try:

        # Create optimizers
        opt_dcgan = Adam(lr=learning_rate,
                         beta_1=beta_1, beta_2=beta_2, epsilon=1e-08)
        opt_discriminator = Adam(lr=learning_rate,
                                 beta_1=beta_1, beta_2=beta_2,
                                 epsilon=1e-08)

        generator_model.compile(loss='mae', optimizer=opt_discriminator)
        discriminator_model.trainable = False

        GAN_model = models.GAN(generator_model, discriminator_model, img_dim)

        loss = [l1_loss, 'binary_crossentropy']
        loss_weights = [l1_weight, 1]
        GAN_model.compile(loss=loss, loss_weights=loss_weights,
                          optimizer=opt_dcgan)

        discriminator_model.trainable = True
        discriminator_model.compile(loss='binary_crossentropy',
                                    optimizer=opt_discriminator)

        # Start training
        for e in range(1, nb_epoch + 1):
            print(f'Epoch {e}/{nb_epoch}')
            batch_counter = 1

            for X_full_batch, X_sketch_batch in data_utils.gen_batch(X_full_train, X_sketch_train, batch_size):
                print(f'Batch {batch_counter}/{batches_per_e}')
                # Create a batch to feed the discriminator model
                X_disc, y_disc = data_utils.get_disc_batch(X_full_batch,
                                                           X_sketch_batch,
                                                           generator_model,
                                                           batch_counter)

                # Update the discriminator
                disc_loss = discriminator_model.train_on_batch(X_disc, y_disc)

                # Create a batch to feed the generator model
                X_gen_target, X_gen = X_full_batch, X_sketch_batch
                y_gen = np.ones((X_gen.shape[0], 1), dtype=np.uint8)

                # Freeze the discriminator
                discriminator_model.trainable = False
                gen_loss = GAN_model.train_on_batch(X_gen,
                                                    [X_gen_target, y_gen])
                # Unfreeze the discriminator
                discriminator_model.trainable = True

                # In the last iteration and if epoch is multiple of image
                # saving interval
                if batch_counter == batches_per_e and e % fig_save_epoch == 0:
                    # Save figures
                    figures_dir = os.path.join(experiment_dir, 'figures')
                    # At the end of each epoch save images for visualization
                    # Get new images from validation
                    data_utils.plot_generated_batch(X_full_batch,
                                                    X_sketch_batch,
                                                    generator_model,
                                                    "training",
                                                    figures_dir, e)

                    idx = np.random.choice(X_full_val.shape[0], batch_size,
                                           replace=False)
                    data_utils.plot_generated_batch(X_full_val[idx],
                                                    X_sketch_val[idx],
                                                    generator_model,
                                                    "validation",
                                                    figures_dir, e)

                # In the last batch also log metrics
                if batch_counter == batches_per_e:
                    _run.log_scalar('d.logloss', disc_loss, e)
                    _run.log_scalar('g.tot', gen_loss[0], e)
                    _run.log_scalar('g.l1', gen_loss[1], e)
                    _run.log_scalar('g.logloss', gen_loss[2], e)

                batch_counter += 1

            if e % model_save_epoch == 0:
                models_dir = os.path.join(experiment_dir, 'models')
                gen_weights_path = os.path.join(models_dir,
                                                'gen_weights_epoch%s.h5' % e)
                generator_model.save_weights(gen_weights_path, overwrite=True)

                disc_weights_path = os.path.join(models_dir,
                                                 'disc_weights_epoch%s.h5' % e)
                discriminator_model.save_weights(disc_weights_path,
                                                 overwrite=True)

                GAN_weights_path = os.path.join(models_dir,
                                                'GAN_weights_epoch%s.h5' % e)
                GAN_model.save_weights(GAN_weights_path, overwrite=True)

        # Clear GPU + RAM
        K.clear_session()
        del GAN_model
        del generator_model
        del discriminator_model
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    # Launch training
    #train(**d_params)
    # train(
    #     generator='generator_unet_upsampling',
    #     discriminator='DCGAN_discriminator',
    #     batch_size=4,
    #     nb_epoch=10,
    #     dset='facades',
    #     base_dir='../../',
    #     experiment_name='exp1',
    #     model_save_epoch=5,
    #     fig_save_epoch=2
    # )
    pass
