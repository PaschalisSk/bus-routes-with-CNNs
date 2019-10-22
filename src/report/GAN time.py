import pprint

import pymongo

myclient = pymongo.MongoClient(
    'mongodb+srv://paschalis:A4EVpD3oKzwgeFZ4@busgan-x5lhw.gcp.mongodb.net/test?retryWrites=true&w=majority')
mydb = myclient['busgan']
runs = mydb['runs']
metrics = mydb['metrics']

GAN_q = {'status': 'COMPLETED',
         'config.train_cnf.dset': 'routes_256',
         'config.train_cnf.reverse_dset': {'$ne': 1}
         }

durations_4 = []
durations_0 = []
durations_4u = []
durations_0u = []
for doc in runs.find(GAN_q):
    start_time = doc['start_time']
    stop_time = doc['stop_time']
    if doc['config']['generator_cnf']['nb_conv'] == 0:
        if doc['config']['train_cnf']['generator'] == 'generator_unet_upsampling':
            durations_0u.append((stop_time - start_time).seconds)
        else:
            durations_0.append((stop_time - start_time).seconds)
    else:
        if doc['config']['train_cnf']['generator'] == 'generator_unet_upsampling':
            durations_4u.append((stop_time - start_time).seconds)
        else:
            durations_4.append((stop_time - start_time).seconds)

average_d = sum(durations) / len(durations)
print('deb')
