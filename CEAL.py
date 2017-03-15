from CNN import *
from informative import entropyrank
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import tflearn.datasets.mnist as mnist
import numpy as np
import tensorflow as tf

"""

    DU (duX, duY): Unlabeled training set
    DL (dlX, dlY): Labeled training set
    DH (dhX, dhY): Pseudo-annotation list

    thresh: Hight confidence threshold
    t0: Initial threshold
    dr: Decay rate

    K: Number of uncertain samples
    T: Max. iterations

    DATA: mnist aproximation: (Train Set = 55000)
    DL = 500 / DU = 54500

"""
ndl=600
X, Y, testX, testY = mnist.load_data(one_hot=True)
X = X.reshape([-1, 28, 28, 1])
test_x = testX.reshape([-1, 28, 28, 1])

dlX = X[0:ndl]
dlY = Y[0:ndl]
duX = X[ndl:len(X)]
duY = Y[ndl:len(Y)]

"""

(1) Initialization:

    - Create model
    - Use DL to initialize CNN parameters (Training)

"""
model = network()
model = train(model, dlX, dlY, testX, testY)

"""

(2) Complementary sample selection:

    - Obtain DU predicitons from CNN model
    - Apply [uncertain_list, certain_list] = entropyrank(pred, thresh)

    Uncertain list:
    - Select K samples
    - Oracle annotation
    - Add to DL

    Certain list:
    - Pseudo annotation
    - Add to DH

"""
#Get predictions
nclasses=10

predictions = np.zeros([len(duX),nclasses])
print("Calculating predictions ...")

for i in range(0,len(duX)):

    predictions[i] = model.predict([duX[i]])[0]

    if(i%10000 == 0):
        print(str(i)+"/"+str(len(duX)))

print(str(i+1) + "/" + str(len(duX)))

uncert, cert, en = entropyrank(predictions)

print("N certaintly: "+str(len(cert)))

#The fist K uncertain list samples, labeled by oracle. In MNIST case, asing train labels (duY)
K=200
oracleX = duX[uncert[0:K]]
oracleY = duY[uncert[0:K]]

#Certain list, pseudo-anotation
dhX = duX[cert]
dhY = np.zeros([len(cert),nclasses])
for i in range (0,len(cert)):
    dhY[i][np.argmax(predictions[cert[i]])] = 1

newdlX = np.concatenate((dlX,oracleX,dhX))
newdlY = np.concatenate((dlY,oracleY,dhY))
"""
(3) Training

    - Train net with DL and DH
    - Delete DH
    - Update threshold
"""
print("without autoanotate:")
model = train(model, newdlX, newdlY, testX, testY)

"""
(*) While T not reached, go back to (2)

"""