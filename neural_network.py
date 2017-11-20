import cv2
import numpy as np
import os
from random import shuffle
from tqdm import tqdm
import matplotlib.pyplot as plt
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import tensorflow as tf

TRAIN_DIR = 'C:\\Users\\leonardo.zanella\\Documents\\machine_learning_sentdex\\train'
TEST_DIR = 'C:\\Users\\leonardo.zanella\\Documents\\machine_learning_sentdex\\test'
IMG_SIZE = 50
LR = 1e-3

MODEL_NAME = 'dogvscats-{}-{}.model'.format(LR,'6conv-basic')

def label_imb(img):
    world_label = img.split('.')[-3]
    if world_label == 'cat' : return [1,0]
    elif world_label == 'dog':return [0,1]


def create_train_data():
    train_data = []
    for img in tqdm(os.listdir(TRAIN_DIR)):
        label = label_imb(img)
        path = os.path.join(TRAIN_DIR,img)
        img = cv2.resize(cv2.imread(path,cv2.IMREAD_GRAYSCALE),(IMG_SIZE,IMG_SIZE) )
        train_data.append([np.array(img),np.array(label)])
    shuffle(train_data)
    np.save('train_data.npy',train_data)
    return train_data


def process_test_data():
    testing_data = []
    for img in tqdm(os.listdir(TEST_DIR)):
        path = os.path.join(TEST_DIR, img)
        img_num = img.split('.')[0]
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        testing_data.append([np.array(img), img_num])

    shuffle(testing_data)
    np.save('test_data.npy', testing_data)
    return testing_data


def get_train_data(type):
    if type =='train':
        train_data = create_train_data()
    else:
        train_data = np.load('train_data.npy')
    return train_data


def get_test_data(type):
    if type == 'train':
        test_data = process_test_data()
    else:
        test_data = np.load('test_data.npy')
    return test_data


def CNN():
    tf.reset_default_graph()

    convnet = input_data(shape=[None, IMG_SIZE, IMG_SIZE, 1], name='input')

    convnet = conv_2d(convnet, 32, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 64, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 32, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 64, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 32, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 64, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = fully_connected(convnet, 1024, activation='relu')
    convnet = dropout(convnet, 0.8)

    convnet = fully_connected(convnet, 2, activation='softmax')
    convnet = regression(convnet, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(convnet, tensorboard_dir='log')

    if os.path.exists('{}.meta'.format(MODEL_NAME)):
        model.load(MODEL_NAME)
        print('model Loaded')

    return model


def fit_model(model,train_data):
    train = train_data[:-5000]
    test = train_data[-5000:]

    X = np.array([i[0] for i in train]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    Y = [i[1] for i in train]

    test_x = np.array([i[0] for i in test]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    test_y = [i[1] for i in test]
    model.fit({'input': X}, {'targets': Y}, n_epoch=10, validation_set=({'input': test_x}, {'targets': test_y}),
              snapshot_step=1000, show_metric=True, run_id=MODEL_NAME)

    model.save(MODEL_NAME)


def predict_model(model,test_data):
    fig = plt.figure()

    for num, data in enumerate(test_data[:12]):
        # cat = [1,0]
        # dog = [0,1]
        img_num = data[1]
        img_data = data[0]

        y = fig.add_subplot(3,4,num+1)
        orig = img_data
        data =img_data.reshape(IMG_SIZE,IMG_SIZE,1)

        model_out = model.predict([data])[0]
        if np.argmax(model_out) == 1 :str_label = 'Dog'
        else: str_label = 'Cat'

        y.imshow(orig,cmap ='gray')
        plt.title(str_label)
        y.axes.get_xaxis().set_visible(False)
        y.axes.get_yaxis().set_visible(False)
    plt.show()

def predict_my_image(model,path):
    # fig = plt.figure()
    img_orig = cv2.imread(path, cv2.IMREAD_COLOR)
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = np.array(img)
    data = img.reshape(IMG_SIZE, IMG_SIZE, 1)
    model_out = model.predict([data])[0]
    if np.argmax(model_out) == 1:
        str_label = 'Dog'
    else:
        str_label = 'Cat'
    # y = fig.add_subplot(3, 4, 1)
    plt.imshow(img_orig,cmap='hsv')
    plt.title(str_label)
    # y.axes.get_xaxis().set_visible(False)
    # y.axes.get_yaxis().set_visible(False)
    plt.show()


##################################################

train_data = get_train_data('load')

test_data = get_test_data('load')

model = CNN()

# fit_model(model,train_data)

# predict_model(model,test_data)

predict_my_image(model,'D:\\dog3.jpg')





