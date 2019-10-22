import itertools

from exp import ex

if __name__ == "__main__":
    unet_cnf = {
        #'nb_filters': [16, 32, 64],
        'nb_filters': [32],
        'nb_conv': [4],
        'kernel_size': [(3, 3)],
        'strides': [(1, 1)],
        'kernel_init': ["he_normal"],
        'kernel_init_mean': [None],
        'kernel_init_stddev': [None],
        'padding': ["same"],
        'up_conv_drop_layers': [None],
        'leaky_relu': [None],
        'pool_size': [(2, 2)],
    }

    train_cnf = {
        'generator': ['unet_upsampling'],
        'batch_size': [10],
        'max_epochs': [100],
        'patience': [3],
        'loss': ['focal_loss'],
        #'learning_rate': [0.0005, 0.0001, 0.00005],
        'learning_rate': [0.0001],
        #'beta_1': [0.9, 0.75, 0.5],
        'beta_1': [0.9],
        'beta_2': [0.999],
        'dset': ['routes_256'],
        'base_dir': ['../../'],
        'fig_save_freq': [2],
        'fig_pairs': [3]
    }

    cnf = {
        'generator_cnf': unet_cnf,
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
        print(f'Running experiment {exp_counter}/{total_exp}')
        ex.run(config_updates=config_updates, options=run_options)

        exp_counter += 1
