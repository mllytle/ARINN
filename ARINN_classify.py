import sys, os, random
import tensorflow as tf
from keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from keras.layers import Dense
from keras import Model
import numpy as np
from imageio import imread
from skimage.transform import resize
from pathlib import Path
import matplotlib.pyplot as plt

#throw at me a input image, I will try to tell you whether it has atmospheric river (AR) in it:

#enter the image:

#readin the image:
# var=input("Enter file name to be checked:")
# filepath='/media/data13/ybai/tpw_npp/croped/'+var
# print(filepath)

## Select image and ARINN Version
plot_flag = 1
trial_num = 25
img_id = '20190815T000000.png25' #'20181211T000000.png'
    #random.choice(os.listdir("/media/madison/PASSPORTBLU/croped"))
    # 'AR/mirs_adv_npoess_npp_atms_glb_20210904_tpw_all_as.pngcrop.png'
filepath = '/media/madison/PASSPORTBLU/tempestd_croped/' +img_id
#filepath = '/media/madison/PASSPORTBLU/croped/' +img_id
    #'/media/madison/PASSPORTBLU/croped/' +img_id

rev_num = '3'
savepath = '/media/madison/PASSPORTBLU/'

## Get Image
im = imread(filepath)
im = im[:,:,:3] # crop borders, remove alpha value
im = preprocess_input(im)
im = resize(im, output_shape=(224,224))

# Classify
ARINN = tf.keras.models.load_model(savepath+'ARINN_v'+rev_num)
testdata = np.empty((1, 224, 224, 3))
if plot_flag:
    plt.imshow(im)
    plt.show()
testdata[0]=im
print('This is what I think: 0=AR, 1=NO')
for ii in range(trial_num):
    print(np.argmax(ARINN.predict(testdata), axis=1))