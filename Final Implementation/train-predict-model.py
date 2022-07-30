import numpy as np
import keras
from keras import preprocessing
import keras.backend as K
from keras.callbacks import ModelCheckpoint


model = keras.models.Sequential([
    keras.layers.Conv2D(32,(3,3),activation = "relu" , input_shape = (50,50,3)) ,
    keras.layers.MaxPooling2D(2,2),
    keras.layers.Conv2D(48,(3,3),activation = "relu") ,
    keras.layers.MaxPooling2D(2,2),
    keras.layers.Dropout(0.25),
    keras.layers.Conv2D(64,(3,3),activation = "relu") ,
    keras.layers.MaxPooling2D(2,2),
    keras.layers.Conv2D(96,(3,3),activation = "relu") ,
    keras.layers.MaxPooling2D(2,2),
    keras.layers.Dropout(0.25),
    keras.layers.Flatten(), 
    keras.layers.Dense(256,activation ="relu"),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(2, activation = "softmax"),
    keras.layers.Flatten()

])


def sensitivity(y_true, y_pred): 
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    return true_positives / (possible_positives + K.epsilon())


def specificity(y_true, y_pred):
    true_negatives = K.sum(K.round(K.clip((1 - y_true) * (1 - y_pred), 0, 1)))
    possible_negatives = K.sum(K.round(K.clip(1 - y_true, 0, 1)))
    return true_negatives / (possible_negatives + K.epsilon())


def conditional_average_metric(y_true, y_pred):
    spec = specificity(y_true, y_pred)
    sens = sensitivity(y_true, y_pred)

    minimum = K.minimum(spec, sens)
    condition = K.less(minimum, 0.5)

    multiplier = 0.001
    # This is the constant used to substantially lower
    # the final value of the metric and it can be set to any value
    # but it is recommended to be much lower than 0.5

    result_greater = 0.5 * (spec + sens)
    result_lower = multiplier * (spec + sens)
    result = K.switch(condition, result_lower, result_greater)

    return result


model.compile(
  optimizer='adam', 
  loss = "sparse_categorical_crossentropy",
  metrics=['accuracy', conditional_average_metric, specificity, sensitivity]
  )


train_datagen = preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

test_datagen = preprocessing.image.ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
        '../train',
        target_size=(50, 50),
        batch_size=8,
        class_mode='binary')

validation_generator = test_datagen.flow_from_directory(
        '../test',
        target_size=(50, 50),
        batch_size=8,
        class_mode='binary')


monitor = 'val_conditional_average_metric'

checkpoint = ModelCheckpoint(
  "../models", 
  monitor=monitor, 
  verbose=1, 
  save_best_only=True, 
  mode='max'
  )

callbacks_list = [checkpoint]

model.fit(
    train_generator, 
    epochs=10, 
    validation_data=validation_generator,
    callbacks=callbacks_list
    )

model = keras.models.load_model(
  "../models", 
  custom_objects = {
    'conditional_average_metric': conditional_average_metric, 
    'specificity': specificity, 
    'sensitivity': sensitivity
    })


def predict(file):
  x = preprocessing.image.image_utils.load_img(file, target_size=(50,50))
  x = preprocessing.image.image_utils.img_to_array(x)
  x = np.expand_dims(x, axis=0)
  array = model.predict(x)
  result = array[0]

  if result[0] > result[1]:
    if result[0] > 0.9:
      print("Prediction: Stock prices will decrease.")
      answer = 'buy'

    else:
      print("Prediction: Not confident")
      answer = 'n/a'

  else:
    if result[1] > 0.9:
      print("Prediction: Stock prices will increase.")
      answer = 'sell'

    else:
      print("Prediction: Not confident")
      answer = 'n/a'

  return answer


predict("../test/predict/chart1.png")
