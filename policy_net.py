import pandas as pd
import shutil
import chainer
from chainer import functions as F
from chainer import links as L
from chainer import Variable
from chainer import optimizers
import argparse
from chainer import cuda
import os
from sklearn.model_selection import KFold
import time
from sklearn.externals import joblib
import numpy as np
class CNN(chainer.Chain):
    def __init__(self, n_channel, N , K,initializer=None):
        n_out = N**2
        super(CNN, self).__init__()
        self.n_channel = n_channel
        n_filter = 16
        self.N = N
        n_hidden = 2 * n_out

        with self.init_scope():
            # the size of the inputs to each layer will be inferred
            self.l1 = L.Convolution2D(None, n_filter, ksize=K, pad=0, nobias=True,initialW = initializer)
            #self.l1 = L.Linear(None, n_units)  # n_in -> n_units
            self.l2 = L.Linear(None, n_hidden,initialW = initializer)  # n_in -> n_units
            self.l3 = L.Linear(None, n_out,initialW = initializer)  # n_units -> n_units
    def __call__(self, x, mask, t):
        x = x.reshape(-1,self.n_channel,self.N,self.N)
        mask = mask.reshape(-1,self.N**2)
        h1 = F.relu(self.l1(x))
        #print (h1.shape)
        h2 = F.relu(self.l2(h1))

        #o = F.softmax(self.l3(h2)-mask)
        #return F.softmax_cross_entropy(o,t,reduce="no")

        o = F.softmax(self.l3(h2))
        r = o * mask
        r = r/r.data.sum()
        return F.softmax_cross_entropy((self.l3(h2) *  mask)/r.data.sum(),t,reduce="no")

    def predict(self, x, mask):
        x = x.reshape(-1,self.n_channel,self.N,self.N)
        mask = mask.reshape(-1,self.N**2)

        h1 = F.relu(self.l1(x))
        h2 = F.relu(self.l2(h1))

        # o = F.softmax(self.l3(h2)-mask)
        # return o

        o = F.softmax(self.l3(h2))
        r = o * mask
        r = r/r.data.sum()
        return r
