import itertools

from exp import ex

if __name__ == "__main__":
    gen_cnf = {
        'nb_filters': [64],
        'nb_conv': [0],
        'kernel_size': [(4, 4)],
        'strides': [(2, 2)],
        'kernel_init': ["RandomNormal"],
        'kernel_init_mean': [0.0],
        'kernel_init_stddev': [0.02],
        'padding': ["same"],
        'up_conv_drop_layers': [2],
        'leaky_relu': [1] # Boolean here, 0 for False, 1 for True
    }

    disc_cnf = {
        'nb_filters': [64],
        'nb_conv': [0],
        'kernel_size': [(4, 4)],
        'strides': [(2, 2)],
        'kernel_init': ["RandomNormal"],
        'kernel_init_mean': [0.0],
        'kernel_init_stddev': [0.02],
        'padding': ["same"]
    }

    train_cnf = {
        'generator': ['generator_unet_upsampling'],
        'discriminator': ['DCGAN_discriminator'],
        'batch_size': [4],
        'nb_epoch': [10],
        'learning_rate': [2e-4],
        'beta_1': [0.5],
        'beta_2': [0.999],
        'l1_weight': [10],
        'dset': ['routes_256'],
        'base_dir': ['../../'],
        'fig_save_epoch': [2],
        'reverse_dset': [0]
    }

    cnf = {
        'generator_cnf': gen_cnf,
        'discriminator_cnf': disc_cnf,
        'train_cnf': train_cnf
    }

    # https://stackoverflow.com/questions/50606454/cartesian-product-of-nested-dictionaries-of-lists
    def gen_combinations(d):
        keys, values = d.keys(), d.values()
        combinations = itertools.product(*values)

        for c in combinations:
            yield dict(zip(keys, c))

    def gen_dict_combinations(d):
        keys, values = d.keys(), d.values()
        for c in itertools.product(*(gen_combinations(v) for v in values)):
            yield dict(zip(keys, c))

    # Create a list of all possible combinations of the values in the arrays
    # in the dictionaries
    cnf_grid = list(gen_dict_combinations(cnf))

    run_options = {
        '--capture': 'no',
        '--loglevel': 40
    }
    exp_counter = 1
    total_exp = len(cnf_grid)
    for config_updates in cnf_grid:
        # Save model weights 1 times per run
        config_updates.get('train_cnf')['model_save_epoch'] = \
            config_updates.get('train_cnf').get('nb_epoch')

        print(f'Running experiment {exp_counter}/{total_exp}')
        ex.run(config_updates=config_updates, options=run_options)

        exp_counter += 1
