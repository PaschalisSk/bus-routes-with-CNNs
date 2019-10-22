import pymongo

myclient = pymongo.MongoClient('mongodb+srv://paschalis:A4EVpD3oKzwgeFZ4@busgan-x5lhw.gcp.mongodb.net/test?retryWrites=true&w=majority')
mydb = myclient['unet']
runs = mydb['runs']
metrics = mydb['metrics']

pipeline = [
    {
        '$match': {
            'name': 'val_loss'
        }
    }, {
        '$addFields': {
            'min_value': {
                '$min': '$values'
            }
        }
    }, {
        '$addFields': {
            'min_index': {
                '$indexOfArray': [
                    '$values', '$min_value'
                ]
            }
        }
    }, {
        '$addFields': {
            'min_epoch': {
                '$add': [
                    '$min_index', 1
                ]
            },
            'min_timestamp': {
                '$arrayElemAt': [
                    '$timestamps', '$min_index'
                ]
            }
        }
    }, {
        '$lookup': {
            'from': 'runs',
            'localField': 'run_id',
            'foreignField': '_id',
            'as': 'run'
        }
    }, {
        '$unwind': {
            'path': '$run'
        }
    }, {
        '$match': {
            'run.status': 'COMPLETED'
        }
    }, {
        '$sort': {
            'min_value': 1
        }
    }, {
        '$addFields': {
            'min_time': {
                '$divide': [
                    {
                        '$subtract': [
                            '$min_timestamp', '$run.start_time'
                        ]
                    }, 1000
                ]
            }
        }
    }
]

import pandas as pd
results_df = pd.DataFrame(columns=['run_id', 'learning_rate', 'beta_1',
                                   'nb_filters', 'time', 'epochs', 'val_loss'])
mydoc = metrics.aggregate(pipeline)
for result in mydoc:
    data = {
        'run_id': int(result['run_id']),
        'learning_rate': result['run']['config']['train_cnf']['learning_rate'],
        'beta_1': result['run']['config']['train_cnf']['beta_1'],
        'nb_filters': result['run']['config']['generator_cnf']['nb_filters'],
        'time': result['min_time'],
        'epochs': result['min_epoch'],
        'val_loss': result['min_value'],
    }
    results_df = results_df.append(data, ignore_index=True)

results_df['run_id'] = pd.to_numeric(results_df['run_id'], downcast='integer')
results_df['nb_filters'] = pd.to_numeric(results_df['nb_filters'], downcast='integer')
results_df['epochs'] = pd.to_numeric(results_df['epochs'], downcast='integer')
results_df.to_csv('../../output/mongo_csv/unet.csv', index=False,
                  float_format='%.6f')
