import numpy as np
from keras.initializers import RandomNormal
from keras.layers import Input, Concatenate
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import Conv2D, UpSampling2D
from keras.layers.core import Flatten, Dropout, Activation, Dense
from keras.layers.normalization import BatchNormalization
from keras.models import Model


def generator_upsampling(img_dim, nb_filters, nb_conv,
                         kernel_size, strides,
                         kernel_init, kernel_init_mean,
                         kernel_init_stddev, padding,
                         up_conv_drop_layers, leaky_relu):
    nb_channels = img_dim[-1]

    if nb_conv == 0:
        min_s = min(img_dim[:-1])
        nb_conv = int(np.floor(np.log(min_s) / np.log(2)))

    if kernel_init == 'RandomNormal':
        kernel_initializer = RandomNormal(kernel_init_mean, kernel_init_stddev)

    def conv_block(x, nb_f, name, bn):
        x = Conv2D(nb_f, kernel_size,
                   strides=strides, name=name, padding=padding,
                   kernel_initializer=kernel_initializer)(x)
        if bn:
            x = BatchNormalization(axis=-1)(x)
        if leaky_relu == 1:
            x = LeakyReLU(0.2)(x)
        else:
            x = Activation("relu")(x)
        return x

    unet_input = Input(shape=img_dim, name="unet_input")

    # Max 512 filters
    list_nb_filters = [nb_filters * min(8, (2 ** i)) for i in range(nb_conv)]

    # Encoder
    list_encoder = []
    for i, nb_f in enumerate(list_nb_filters, 1):
        name = "unet_conv2D_%s" % i
        if len(list_encoder) == 0:
            x = conv_block(unet_input, nb_f, name, False)
        else:
            x = conv_block(list_encoder[-1], nb_f, name, True)
        list_encoder.append(x)

    def up_conv_block(x, nb_f, name, dropout):
        x = UpSampling2D(size=strides)(x)
        x = Conv2D(nb_f, kernel_size, name=name, padding=padding,
                   kernel_initializer=kernel_initializer)(x)
        x = BatchNormalization(axis=-1)(x)
        if dropout:
            x = Dropout(0.5)(x)
        x = Activation("relu")(x)
        return x

    # Prepare decoder filters
    list_nb_filters = list_nb_filters[:-1][::-1]

    # Decoder
    list_decoder = []
    for i, nb_f in enumerate(list_nb_filters):
        name = "unet_upconv2D_%s" % (i + 1)
        # Dropout only on first 2 layers
        if i < up_conv_drop_layers:
            dropout = True
        else:
            dropout = False
        if len(list_decoder) == 0:
            x = up_conv_block(list_encoder[-1],
                              nb_f, name, dropout)
        else:
            x = up_conv_block(list_decoder[-1],
                              nb_f, name, dropout)
        list_decoder.append(x)

    x = UpSampling2D(size=strides)(list_decoder[-1])
    x = Conv2D(nb_channels, kernel_size, name="last_conv", padding=padding,
               kernel_initializer=kernel_initializer)(x)
    x = Activation("tanh")(x)

    generator_unet = Model(inputs=[unet_input], outputs=[x],
                           name='generator_unet_upsampling')

    return generator_unet


def generator_unet_upsampling(img_dim, nb_filters, nb_conv,
                              kernel_size, strides,
                              kernel_init, kernel_init_mean,
                              kernel_init_stddev, padding,
                              up_conv_drop_layers, leaky_relu):
    nb_channels = img_dim[-1]

    if nb_conv == 0:
        min_s = min(img_dim[:-1])
        nb_conv = int(np.floor(np.log(min_s) / np.log(2)))

    if kernel_init == 'RandomNormal':
        kernel_initializer = RandomNormal(kernel_init_mean, kernel_init_stddev)

    def conv_block(x, nb_f, name, bn):
        x = Conv2D(nb_f, kernel_size,
                   strides=strides, name=name, padding=padding,
                   kernel_initializer=kernel_initializer)(x)
        if bn:
            x = BatchNormalization(axis=-1)(x)
        if leaky_relu == 1:
            x = LeakyReLU(0.2)(x)
        else:
            x = Activation("relu")(x)
        return x

    unet_input = Input(shape=img_dim, name="unet_input")

    # Max 512 filters
    list_nb_filters = [nb_filters * min(8, (2 ** i)) for i in range(nb_conv)]

    # Encoder
    list_encoder = []
    for i, nb_f in enumerate(list_nb_filters, 1):
        name = "unet_conv2D_%s" % i
        if len(list_encoder) == 0:
            x = conv_block(unet_input, nb_f, name, False)
        else:
            x = conv_block(list_encoder[-1], nb_f, name, True)
        list_encoder.append(x)

    def up_conv_block_unet(x, x2, nb_f, name, dropout):
        x = UpSampling2D(size=strides)(x)
        x = Conv2D(nb_f, kernel_size, name=name, padding=padding,
                   kernel_initializer=kernel_initializer)(x)
        x = BatchNormalization(axis=-1)(x)
        if dropout:
            x = Dropout(0.5)(x)
        x = Activation("relu")(x)
        x = Concatenate(axis=-1)([x, x2])
        return x

    # Prepare decoder filters
    list_nb_filters = list_nb_filters[:-1][::-1]

    # Decoder
    list_decoder = []
    for i, nb_f in enumerate(list_nb_filters):
        name = "unet_upconv2D_%s" % (i + 1)
        # Dropout only on first 2 layers
        if i < up_conv_drop_layers:
            dropout = True
        else:
            dropout = False
        if len(list_decoder) == 0:
            x = up_conv_block_unet(list_encoder[-1], list_encoder[-2],
                                   nb_f, name, dropout)
        else:
            x = up_conv_block_unet(list_decoder[-1], list_encoder[-(i + 2)],
                                   nb_f, name, dropout)
        list_decoder.append(x)

    x = UpSampling2D(size=strides)(list_decoder[-1])
    x = Conv2D(nb_channels, kernel_size, name="last_conv", padding=padding,
               kernel_initializer=kernel_initializer)(x)
    x = Activation("tanh")(x)

    generator_unet = Model(inputs=[unet_input], outputs=[x],
                           name='generator_unet_upsampling')

    return generator_unet


def DCGAN_discriminator(img_dim, nb_filters, nb_conv,
                        kernel_size, strides,
                        kernel_init, kernel_init_mean,
                        kernel_init_stddev, padding):
    if nb_conv == 0:
        min_s = min(img_dim[:-1])
        nb_conv = int(np.floor(np.log(min_s) / np.log(2)))

    if kernel_init == 'RandomNormal':
        kernel_initializer = RandomNormal(kernel_init_mean, kernel_init_stddev)

    list_filters = [nb_filters * min(8, (2 ** i)) for i in range(nb_conv)]

    disc_input = Input(shape=img_dim, name="disc_input")
    x = Conv2D(list_filters[0], kernel_size, strides=strides,
               name="disc_conv2d_1", padding=padding,
               kernel_initializer=kernel_initializer)(disc_input)
    x = LeakyReLU(0.2)(x)

    # Next convs
    for i, nb_f in enumerate(list_filters[1:], 2):
        name = "disc_conv2d_%s" % i
        x = Conv2D(nb_f, kernel_size, strides=strides,
                   name=name, padding=padding,
                   kernel_initializer=kernel_initializer)(x)
        x = BatchNormalization(axis=-1)(x)
        x = LeakyReLU(0.2)(x)

    # Can't use the convolution from the pix2pix paper coz we won't always end
    # up with 1x1xfilters dimensions if we use less conv layers
    # x = Conv2D(1, kernel_size, strides=(1, 1), name="extra_conv",
    #            padding=padding, kernel_initializer=kernel_initializer)(x)
    # x = Activation("sigmoid")(x)
    # x = Flatten()(x)
    x = Flatten()(x)
    x = Dense(1, name="disc_dense", kernel_initializer=kernel_initializer)(x)
    x = Activation("sigmoid")(x)

    discriminator_model = Model(inputs=disc_input, outputs=[x],
                                name='DCGAN_discriminator')

    return discriminator_model


def GAN(generator, discriminator, img_dim):
    gen_input = Input(shape=img_dim, name="DCGAN_input")

    generated_image = generator(gen_input)
    GAN_output = discriminator(generated_image)

    GAN = Model(inputs=[gen_input],
                outputs=[generated_image, GAN_output],
                name="GAN")

    return GAN
