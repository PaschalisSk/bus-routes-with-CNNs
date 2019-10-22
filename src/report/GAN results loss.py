import pprint

import pymongo

myclient = pymongo.MongoClient(
    'mongodb+srv://paschalis:A4EVpD3oKzwgeFZ4@busgan-x5lhw.gcp.mongodb.net/test?retryWrites=true&w=majority')
mydb = myclient['busgan']
runs = mydb['runs']
metrics = mydb['metrics']

# GAN_q = {'status': 'COMPLETED',
#          'config.train_cnf.dset': 'routes_256',
#          'config.train_cnf.reverse_dset': {'$ne': 1},
#          'config.generator_cnf.nb_conv': 0,
#          'config.generator_cnf.leaky_relu': 1,
#          'config.train_cnf.l1_weight': 10,
#          'config.train_cnf.generator': 'generator_unet_upsampling',
#          }
#
# total_completed = runs.count(GAN_q)

#id 5 for the above conf
val_dict = {}
for doc in metrics.find():
    #if (doc['run_id'] - 1) % 3 == 0:
    if doc['run_id'] not in val_dict:
        val_dict[doc['run_id']] = {}

    val_dict[doc['run_id']][doc['name']] = doc['values']

pprint.pprint(val_dict)
print('deb')
