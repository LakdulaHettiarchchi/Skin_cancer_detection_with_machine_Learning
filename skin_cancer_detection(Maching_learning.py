# -*- coding: utf-8 -*-
"""Skin_cancer_detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aTKa6GGhki50lv8bcpyjfzIuMhGWHkbk
"""

!pip install -q keras

import keras

from keras.layers import Input, Lambda, Dense, Flatten, MaxPooling2D,Conv2D
from keras.models import Model, Sequential
from keras.applications.vgg16 import VGG16
# from keras.applications.vgg19 import VGG19
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import image
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
import numpy as np
import matplotlib.pyplot as plt
import glob
from keras.layers.normalization import batch_normalization
import os
import seaborn as sns
import cv2
# from keras.models import sequential
# from keras.layers.normalization import BatchNormalization
# from keras.layers.normalization import BatchNormalization
from tensorflow.keras.layers import BatchNormalization

from google.colab import drive
drive.mount('/content/drive/')

!wget /content/drive/MyDrive/archive_4.zip

!unzip /content/drive/MyDrive/archive_4.zip

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

benign_images = getListOfFiles('/content/test/benign')
image.load_img(benign_images[6], target_size=(224,224,3), grayscale=False)

IMAGE_SIZE = 224

train_images = []
train_labels = []

for directory_path in glob.glob("/content/train/*"):
  label = directory_path.split("\\")[-1]
  print(label)
  for img_path in glob.glob(os.path.join(directory_path, '*.jpg')):
    print(img_path)
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (IMAGE_SIZE,IMAGE_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    train_images.append(img)
    train_labels.append(label)

train_images = np.array(train_images)
train_labels = np.array(train_labels)

test_images = []
test_labels = []

for directory_path in glob.glob("/content/test/*"):
  T_label = directory_path.split("\\")[-1]
  print(T_label)
  for img_path in glob.glob(os.path.join(directory_path, '*.jpg')):
    print(img_path)
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (IMAGE_SIZE,IMAGE_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
   
    test_images.append(img)
    # cv2.imshow(img)
    test_labels.append(T_label)

test_images = np.array(test_images)
test_labels = np.array(test_labels)

#Encode Labels from text to integer
from sklearn import preprocessing
le = preprocessing.LabelEncoder()
le.fit(test_labels)
test_lebels_encoded = le.transform(test_labels)
# print(test_lebels_encoded)
le.fit(train_labels)
train_labels_encoded = le.transform(train_labels)
print(train_labels_encoded)

#split dtat into test and train data set 
x_train, y_train, x_test, y_test = train_images, train_labels_encoded, test_images, test_lebels_encoded

#Normalize the fixel value
x_train = x_train / 225.0
x_test  = x_test / 225.0
# print(x_train)

#One hot encoding
from tensorflow.keras.utils import to_categorical
y_train_one_hot = to_categorical(y_train)
y_test_one_hot  = to_categorical(y_test)
print(y_train_one_hot)

VGG_model = VGG16(weights='imagenet', include_top=False, input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3))

for layer in VGG_model.layers:
  layer.trainable = False
VGG_model.summary()

feature_extractor = VGG_model.predict(x_train)
feature = feature_extractor.reshape(feature_extractor.shape[0], -1)

print(feature_extractor.shape)
print("Extracted features:", feature.shape)

x_for_Rf = feature  #reassing the extrated feature in another varaible

from sklearn.ensemble import RandomForestClassifier
RF_model = RandomForestClassifier(n_estimators = 50, random_state = 42)

#train the model on train data
RF_model.fit(x_for_Rf, y_train)

x_test_feature = VGG_model.predict(x_test)
X_test_features = x_test_feature.reshape(x_test_feature.shape[0], -1)

print(x_test_feature.shape)
print(X_test_features.shape)

prediction_RF = RF_model.predict(X_test_features)

prediction_RF = le.inverse_transform(prediction_RF)

from sklearn import metrics
print("Accuracy = ", metrics.accuracy_score(test_labels, prediction_RF))

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(test_labels, prediction_RF)
print(cm)
sns.heatmap(cm, annot=True)

n=np.random.randint(0, x_test.shape[0])
img = x_test[n]
plt.imshow(img)
input_img = np.expand_dims(img, axis=0) #Expand dims so the input is (num images, x, y, c)
input_img_feature=VGG_model.predict(input_img)
input_img_features=input_img_feature.reshape(input_img_feature.shape[0], -1)
prediction_RF = RF_model.predict(input_img_features)[0] 
prediction_RF = le.inverse_transform([prediction_RF])  #Reverse the label encoder to original name
print("The prediction for this image is: ", prediction_RF)
print("The actual label for this image is: ", test_labels[n])