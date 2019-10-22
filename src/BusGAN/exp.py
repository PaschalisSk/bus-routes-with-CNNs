# https://stackoverflow.com/questions/47790619/sacred-python-ex-config-in-one-file-and-ex
from sacred import Experiment
from sacred.observers import MongoObserver

ex = Experiment()

ex.observers.append(MongoObserver.create(
    url='mongodb+srv://paschalis:A4EVpD3oKzwgeFZ4@busgan-x5lhw.gcp.mongodb.net/test?retryWrites=true&w=majority',
    db_name='busgan'))

# Import train now so that the @ex.main in train doesn't throw error
import train


