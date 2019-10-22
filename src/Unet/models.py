import numpy as np
from keras.initializers import RandomNormal, he_normal
from keras.layers import Input, Concatenate
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import Conv2D, UpSampling2D, MaxPooling2D
from keras.layers.core import Flatten, Dropout, Activation, Dense
from keras.layers.normalization import BatchNormalization
from keras.models import Model


def unet_upsampling(img_dim, nb_filters, nb_conv,
                    kernel_size, strides,
                    kernel_init, kernel_init_mean,
                    kernel_init_stddev, padding,
                    up_conv_drop_layers, leaky_relu, pool_size):

    if nb_conv == 0:
        min_s = min(img_dim[:-1])
        nb_conv = int(np.floor(np.log(min_s) / np.log(2)))

    if kernel_init == 'RandomNormal':
        kernel_initializer = RandomNormal(kernel_init_mean, kernel_init_stddev)
    elif kernel_init == 'he_normal':
        kernel_initializer = he_normal()
    else:
        raise ValueError('Kernel init name not recognised')

    def conv_block(x, nb_f, name, max_pooling, dropout):
        if max_pooling:
            x = MaxPooling2D(pool_size=pool_size)(x)

        x = Conv2D(nb_f, kernel_size,
                   strides=strides, name=name + '_1', padding=padding,
                   kernel_initializer=kernel_initializer,
                   activation='relu')(x)
        x = Conv2D(nb_f, kernel_size,
                   strides=strides, name=name + '_2', padding=padding,
                   kernel_initializer=kernel_initializer,
                   activation='relu')(x)

        if dropout:
            x = Dropout(0.5)(x)

        return x

    unet_input = Input(shape=img_dim, name="unet_input")

    # Max 1024 filters
    list_nb_filters = [nb_filters * min(16, (2 ** i)) for i in range(nb_conv)]

    # Encoder
    list_encoder = []
    for i, nb_f in enumerate(list_nb_filters, 1):
        name = "unet_conv2D_%s" % i
        # Dropout only in the last 2 layers
        dropout = False if i < nb_conv - 2 else True

        if len(list_encoder) == 0:
            # Max pooling in all down conv layers except the first one
            x = conv_block(unet_input, nb_f, name,
                           max_pooling=False, dropout=dropout)
        else:
            x = conv_block(list_encoder[-1], nb_f, name,
                           max_pooling=True, dropout=dropout)
        list_encoder.append(x)

    def up_conv_block_unet(x, x2, nb_f, name):
        x = UpSampling2D(size=pool_size)(x)
        x = Conv2D(nb_f, pool_size, name=name + '_1', padding=padding,
                   kernel_initializer=kernel_initializer,
                   activation='relu')(x)
        x = Concatenate(axis=-1)([x, x2])
        x = Conv2D(nb_f, kernel_size, name=name + '_2', padding=padding,
                   kernel_initializer=kernel_initializer,
                   activation='relu')(x)
        x = Conv2D(nb_f, kernel_size, name=name + '_3', padding=padding,
                   kernel_initializer=kernel_initializer,
                   activation='relu')(x)
        return x

    # Prepare decoder filters
    list_nb_filters = list_nb_filters[:-1][::-1]

    # Decoder
    list_decoder = []
    for i, nb_f in enumerate(list_nb_filters):
        name = "unet_upconv2D_%s" % (i + 1)

        if len(list_decoder) == 0:
            x = up_conv_block_unet(list_encoder[-1], list_encoder[-2],
                                   nb_f, name)
        else:
            x = up_conv_block_unet(list_decoder[-1], list_encoder[-(i + 2)],
                                   nb_f, name)
        list_decoder.append(x)

    x = Conv2D(2, (1, 1), name="last_conv", padding=padding,
               kernel_initializer=kernel_initializer,
               activation='relu')(list_decoder[-1])
    x = Conv2D(1, (1, 1), activation='sigmoid')(x)
    # x = Conv2D(1, (1, 1), name="last_conv",
    #            kernel_initializer=kernel_initializer,
    #            activation='sigmoid')(list_decoder[-1])

    unet = Model(inputs=[unet_input], outputs=[x],
                 name='generator_unet_upsampling')
    unet.summary()

    return unet
