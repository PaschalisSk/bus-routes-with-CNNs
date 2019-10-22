from keras.datasets import mnist
import numpy as np

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train[x_train <= 127] = 0
x_train[x_train > 127] = 1
uf, cof = np.unique(x_train, return_counts=True)
print('deb')
