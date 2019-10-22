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

mydoc = metrics.aggregate(pipeline)
#mydoc = runs.find({'experiment.name': 'lstm_sent_trends_batch_size'}).sort([('_id', pymongo.ASCENDING)])
# myquery = {'_id': {'$gt': 747}}
# newvalues = { "$set": { "experiment.name": "lstm_sent_trends_model_conf" } }
# x = runs.update_many(myquery, newvalues)
#
# print(x.modified_count, "documents updated.")
#$$deleteO = metri4cs.delete_many({'run_id': {'$gt': 351}})
#runs.distinct('experiment.name')
#mydoc = runs.find({'_id': 702})
#tags = db.mycoll.find({"category": "movie"}).distinct("tags")
#'lstm_sent_trends_batch_size'
results = list(mydoc)
for result in mydoc:
    #print(result)
    print('Batch size: ' + str(result['_id']['config']['batch_size']))
    print('Learning rate: ' + str(result['_id']['config']['learning_rate']))
    print('Neurons: ' + str(result['_id']['config']['num_neurons']))
    print('Layers: ' + str(result['_id']['config']['num_hidden_layers']))
    mse_avg = str('%.4f' % (10000*result['min_value_avg']))
    mse_sem = str('%.4f' % (10000*result['min_value_sem']))
    # mse_avg = str('%.2f' % result['min_value_avg'])
    # mse_sem = str('%.2f' % result['min_value_sem'])
    print('MSE:' + mse_avg + '\pm' + mse_sem)
    time_avg = str('%.2f' % result['min_time_avg'])
    time_sem = str('%.2f' % result['min_time_sem'])
    print('Time: ' + time_avg + '\pm' + time_sem)
    print('t')

