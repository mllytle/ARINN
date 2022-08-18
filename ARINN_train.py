'''
ARINN Model Creation and Traiing Script
7/29/22
Madison Lytle

Modified from AI_train.py by Dr. Changyong Cao. Notes below are from that script:
	AI/ML model to detect atmospheric river from TPW images on the US west coast region.
	Mobilenet V2 is used and top layer trained.
	Original model was for cat detection from:  
		Sebastiaan Mathôt  https://www.youtube.com/watch?v=8LjK4knsTRQ&t=943s
	Modifications made by Clarence Lam and Changyong Cao, 7/21/2022
	ATMS TPW training data generated by Yan Bai.
	To be expaned to AR detection from Smallsat by Lapenta Intern Madison Lytle.
	Mobilenet V2 was also previously used in urban nightlight study in Cao et al. 2022 (https://www.mdpi.com/2072-4292/14/13/3126) 
'''

## Imports =====================================================
import tensorflow as tf
from keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from keras.layers import Dense
from keras import Model
import numpy as np
#from imageio.v2 import imread
from imageio import imread
from skimage.transform import resize
from pathlib import Path
from keras.utils import to_categorical


## Params =====================================================
# Dir:
basepath = '/media/madison/9704680128/ARINN_hd/sorted_TPW' # PASSPORTBLU/sorted_croped'
	# image data loc ^
savepath = '/media/madison/9704680128/ARINN_hd/models' # PASSPORTBLU/'
	# location to save ARINN model to

# Other:
val_size = 20 # defines number of images reserved for validation
epochs_num = 50 # defines epoch size for training
rev_num = '6' #revision number for ARINN

# Flags
save_flag = 1 # 1 to save model, 0 to not save
check_save_flag = 0

## Set up ARINN + Get Data  =====================================================
model = MobileNetV2(weights='imagenet')#check.

AR = list(Path(basepath).glob("AR/*pngcrop.png"))
NO = list(Path(basepath).glob("NO/*pngcrop.png"))

all_files = AR + NO

data = np.empty((len(all_files), 224, 224, 3)) # 3 layers for rbg values

for i, filepath in enumerate(all_files):
	im = imread(filepath)
	im = im[:,:,:3] # crop borders, remove alpha value
	im = preprocess_input(im)
	im = resize(im, output_shape=(224,224))
	data[i] = im

# Set up labels
labels = np.empty(len(all_files), dtype=int)
labels[:len(AR)] = 0 #0 to len(AR)
labels[len(AR):] = 1 #len(AR) to end
	# labels = to_categorical(labels, 2)

# Create base CNN model
def create_model(model):
	new_output = Dense(2, activation='softmax') #layer with 2 output
	new_output = new_output(model.layers[-2].output) #-2 layer replacing last layer

	new_input = model.input
	new_model = Model(inputs=new_input, outputs=new_output)

	for layer in new_model.layers[:-1]: # only train the last layer
		layer.trainable = False

	new_model.compile(
		optimizer='adam',
		loss='sparse_categorical_crossentropy',
		metrics=['accuracy'] #,
		#run_eagerly=True
	)
	return new_model

ARINN = create_model(model)

# new_model.summary()
ARINN.fit(x=data, y=labels, epochs = epochs_num, verbose=2)
#then predict:
predictions = ARINN.predict(data)
print('Should be AR (0)')
print(np.argmax(predictions[:len(AR)], axis=1))
print('Should be NO (1)')
print(np.argmax(predictions[len(AR):], axis=1))

## Training and validation =====================================================
#split the data, using last 'val_size' for validation; the rest for training
AR_split = len(AR)-val_size
NO_split = len(NO)-val_size

training_data = np.empty((AR_split+NO_split, 224, 224, 3))
validation_data = np.empty((2*val_size, 224, 224, 3))

training_data[:AR_split] = data[:AR_split]
training_data[AR_split:] = data[len(AR):len(AR)+NO_split]

validation_data[:val_size] = data[AR_split:len(AR)]
validation_data[val_size:] = data[len(AR)+NO_split:]

training_labels = np.empty(AR_split+NO_split)
training_labels[:AR_split] = 0
training_labels[AR_split:] = 1

validation_labels = np.empty(2*val_size)
validation_labels[:val_size] = 0
validation_labels[val_size:] = 1

# New model for training and validation:
ARINN_2 = create_model(model)
ARINN_2.fit(x=training_data, y=training_labels, validation_data=(validation_data,validation_labels), epochs=epochs_num, verbose=2)


## Save model =====================================================
# Save the entire model
if save_flag:
	#os.mkdir('/media/madison/PASSPORTBLU/ARINN_v'+rev_num)
	ARINN_2.save(savepath+'ARINN_v'+rev_num)

# Check the saved model
if check_save_flag and save_flag:
	check_save = tf.keras.models.load_model(savepath+'ARINN_v'+rev_num)
	check_save.compile(
			optimizer='adam',
			loss='sparse_categorical_crossentropy',
			metrics=['accuracy']
	)
	check_save.summary()# Check its architecture
