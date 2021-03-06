import tflearn
from tflearn.data_utils import shuffle, to_categorical
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.estimator import regression
from tflearn.data_preprocessing import ImagePreprocessing
from tflearn.data_augmentation import ImageAugmentation
import numpy as np
import tensorflow as tf
import urllib
import os


# Make the image dimensions proper to fit the tf.learn standards.
def get_proper_images(raw):
    raw_float = np.array(raw, dtype=float)
    images = raw_float.reshape([-1, 3, 32, 32])
    images = images.transpose([0, 2, 3, 1])
    return images

# Import the labels (the true class of each image)
def onehot_labels(labels):
    return np.eye(100)[labels]

def unpickle(file):
    import cPickle
    fo = open(file, 'rb')
    dict = cPickle.load(fo)
    fo.close()
    return dict

#Retrieving data
tt = urllib.URLopener()
tt.retrieve("http://kashaaf.com/cifar-100-python/train", "train")
tt.retrieve("http://kashaaf.com/cifar-100-python/test", "test")


X = get_proper_images(unpickle('train')['data'])
Y = onehot_labels(unpickle('train')['fine_labels'])
X_test = get_proper_images(unpickle('test')['data'])
Y_test = onehot_labels(unpickle('test')['fine_labels'])
img_prep = ImagePreprocessing()
img_prep.add_featurewise_zero_center()
img_prep.add_featurewise_stdnorm()
img_aug = ImageAugmentation()
img_aug.add_random_flip_leftright()
img_aug.add_random_rotation(max_angle=15.)
network = input_data(shape=[None, 32, 32, 3],
                     data_preprocessing=img_prep,
                     data_augmentation=img_aug)
network = conv_2d(network, 32, 3, strides=1, padding='same', activation='relu', bias=True, # First layer, with a kernel going over every image.
                  bias_init='zeros', weights_init='uniform_scaling')
network = max_pool_2d(network, 2 , strides=None, padding='same') #This is a downsampling of the image in the spatial dimensions
#                                                               , allowing for assumptions to be made about the features
network = conv_2d(network, 64, 3, strides=1, padding='same', activation='relu', bias=True,
                  bias_init='zeros', weights_init='uniform_scaling')
network = conv_2d(network, 64, 3, strides=1, padding='same', activation='relu', bias=True,
                  bias_init='zeros', weights_init='uniform_scaling')
network = max_pool_2d(network, 2 , strides=None, padding='same')
network = fully_connected(network, 600, activation='relu')
network = dropout(network, 0.5)  # This ignores some of the neurons during training in order to avoid overfitting (Randomly)
network = fully_connected(network, 100, activation='softmax') # The final layer, producing a 100x1 vector of the 100 classes
network = regression(network, optimizer='AdaGrad', # The optimization algorithm that is used as well as the loss function.
                     loss='categorical_crossentropy',
                     learning_rate=0.001)

with tf.device('cpu:0'):
    model = tflearn.DNN(network, tensorboard_verbose=1,tensorboard_dir=os.path.expanduser('~/eventlogs/test8')) # This is the actual training of the network
    model.fit(X, Y, n_epoch=40  , shuffle=True, validation_set=(X_test, Y_test), show_metric=True, batch_size=100 , run_id='aa2') # Here the output is compared
    #                                                                                                                   to the validation set and accuracy is found
