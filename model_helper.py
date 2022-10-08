import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import resnet_v2
import json


def predict(img, model, classes):
    test_image = img.resize((224,224))
    test_image = image.img_to_array(test_image)
    test_image = resnet_v2.preprocess_input(test_image)
    test_image = np.expand_dims(test_image, axis=0)
         
    pred_prob = model.predict(test_image)
    pred_class = classes[pred_prob.argmax()] # find the predicted class   
    result = (pred_class, pred_prob.max())
    
    return result


def load_saved_model(model_file):
    model = load_model(model_file)
    return model


def get_classes(class_file):
    with open(class_file, 'r') as f:
        class_indices = json.load(f)

    class_names = dict((v, k) for k, v in class_indices.items())

    return class_names

