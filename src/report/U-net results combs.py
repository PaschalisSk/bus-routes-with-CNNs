import pprint

import pymongo

myclient = pymongo.MongoClient(
    'mongodb+srv://paschalis:A4EVpD3oKzwgeFZ4@busgan-x5lhw.gcp.mongodb.net/test?retryWrites=true&w=majority')
mydb = myclient['unet']
runs = mydb['runs']
metrics = mydb['metrics']

GAN_q = {'status': 'COMPLETED',
         'config.train_cnf.dset': 'routes_256',
         'config.train_cnf.reverse_dset': {'$ne': 1}
         }
total_completed = mydb['runs'].count(GAN_q)

cnf = {}
for doc in mydb['runs'].find(GAN_q):
    for cnf_k, cnf_v in doc['config'].items():
        if cnf_k == 'seed':
            continue
        if cnf_k not in cnf:
            cnf[cnf_k] = {}
        for inner_cnf_k, inner_cnf_v in doc['config'][cnf_k].items():
            if inner_cnf_k not in cnf[cnf_k]:
                cnf[cnf_k][inner_cnf_k] = set()
            if type(inner_cnf_v) is dict and 'py/tuple' in inner_cnf_v:
                inner_cnf_v = tuple(inner_cnf_v['py/tuple'])
            cnf[cnf_k][inner_cnf_k].add(inner_cnf_v)

pprint.pprint(cnf)
print('deb')
# mydb['runs'].find().forEach(lambda doc: print(doc.config))
