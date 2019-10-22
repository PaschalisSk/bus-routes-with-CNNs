import pymongo

myclient = pymongo.MongoClient('mongodb+srv://paschalis:A4EVpD3oKzwgeFZ4@busgan-x5lhw.gcp.mongodb.net/test?retryWrites=true&w=majority')
mydb = myclient['unet']
runs = mydb['runs']
metrics = mydb['metrics']

a = runs.distinct('config.generator_cnf.nb_conv')
print('deb')
