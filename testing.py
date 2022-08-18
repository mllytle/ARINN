import tensorflow as tf
from keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from keras.layers import Dense
from keras import Model
import numpy as np
#from imageio.v2 import imread
from imageio import imread
from skimage.transform import resize
from pathlib import Path

rev_num = '0' #revision number for ARINN

check_save = tf.keras.models.load_model('/media/madison/PASSPORTBLU/ARINN_v'+rev_num)
check_save.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
)
# Check its architecture
check_save.summary()