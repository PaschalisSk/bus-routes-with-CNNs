import pprint

import pymongo

myclient = pymongo.MongoClient(
    'mongodb+srv://paschalis:A4EVpD3oKzwgeFZ4@busgan-x5lhw.gcp.mongodb.net/test?retryWrites=true&w=majority')
mydb = myclient['unet']
runs = mydb['runs']
metrics = mydb['metrics']

# unet_q = {'status': 'COMPLETED',
#           'config.train_cnf.dset': 'routes_256',
#          }
#
# total_completed = mydb['runs'].count(unet_q)

pipeline = [
    {
        '$match': {
            'name': 'val_loss'
        }
    },
    {
        '$addFields': {
            'min_value': {'$min': '$values'},
        }
    },
    {
        '$addFields': {
            'min_index': {'$indexOfArray': ['$values', '$min_value']}
        }
    },
    {
        '$addFields': {
            'min_epoch': {'$add': ['$min_index', 1]},
            'min_timestamp': {'$arrayElemAt': ['$timestamps', '$min_index']}
        }
    },
    {
        '$lookup': {
            'from': 'runs',
            'localField': 'run_id',
            'foreignField': '_id',
            'as': 'run'
        }
    },
    {
        '$unwind': '$run'
    },
    {
        '$match': {
            'run.config.train_cnf.dset': 'routes_256',
            'run.status': 'COMPLETED'
        }
    },
    {
        '$addFields': {
            'min_time': {
                '$divide': [
                    {'$subtract': ['$min_timestamp', '$run.start_time']},
                    1000
                ]
            }
        }
    }
]

mydocs = metrics.aggregate(pipeline)

n_doc = {}
for doc in mydocs:
    run_id = doc['run']['_id']
    n_doc[run_id] = {}
    n_doc[run_id]['min_index'] = doc['min_index']
    n_doc[run_id]['min_time'] = "{0:.1f}".format(doc['min_time'] / 60)
    n_doc[run_id]['min_value'] = "{0:.4f}".format(doc['min_value'])
    n_doc[run_id]['cp'] = f"({n_doc[run_id]['min_value']}, {n_doc[run_id]['min_time']})"
    n_doc[run_id]['nb_filters'] = doc['run']['config']['generator_cnf']['nb_filters']
    n_doc[run_id]['beta_1'] = doc['run']['config']['train_cnf']['beta_1']
    n_doc[run_id]['learning_rate'] = doc['run']['config']['train_cnf']['learning_rate']

pprint.pprint(n_doc)
#
# from prettytable import PrettyTable
#
# #pprint.pprint(n_doc)
# for init_filters in [16, 32, 64]:
#     x = PrettyTable()
#     x.field_names = ["b1", "0.0005", "0.0001", "0.00005", "avg"]
#     for k, v in n_doc:
#         if v['nb_filters'] == init_filters:
#
#
#         x.add_row(["Adelaide", 1295, 1158259, 600.5])
#         x.add_row(["Brisbane", 5905, 1857594, 1146.4])
#         x.add_row(["Darwin", 112, 120900, 1714.7])
#         x.add_row(["Hobart", 1357, 205556, 619.5])
#         x.add_row(["Sydney", 2058, 4336374, 1214.8])
#         x.add_row(["Melbourne", 1566, 3806092, 646.9])
#         x.add_row(["Perth", 5386, 1554769, 869.4])
#
# print(x)
print('deb')
# mydb['runs'].find().forEach(lambda doc: print(doc.config))
