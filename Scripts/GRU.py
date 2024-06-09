# LSTM and CNN for sequence classification in the IMDB dataset
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras import layers
import numpy as np
import pickle


def convert_to_ndarray(mesures):
    pression_data = mesures[1]
    flexion_data = mesures[2]
    inertie_data = mesures[3]

    date = []
    pression = []
    flexion = []
    x = []
    y = []
    z = []
    for i in range(len(inertie_data)):
        date.append(inertie_data[i].dateCreation)
        pression.append(pression_data[i].valeur)
        flexion.append(flexion_data[i].valeur)
        x.append(inertie_data[i].X)
        y.append(inertie_data[i].Y)
        z.append(inertie_data[i].Z)

    return np.ndarray([pression, flexion, x, y, z])

def train_LSTM(train_data, test_data):
    # fix random seed for reproducibility
    tf.random.set_seed(7)

    (x_train, y_train), (x_test, y_test) = train_data, test_data
    
    # truncate and pad input sequences
    """max_review_length = 5000
    X_train = sequence.pad_sequences(X_train, maxlen=max_review_length)
    X_test = sequence.pad_sequences(X_test, maxlen=max_review_length)"""
    
    # create the model
    model = keras.Sequential()
    model.add(layers.GRU(64, input_shape=(28, 28)))
    model.add(layers.BatchNormalization())
    model.add(layers.Dense(10))
    print(model.summary())

    mnist = keras.datasets.mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train/255.0, x_test/255.0
    x_validate, y_validate = x_test[:-10], y_test[:-10]
    x_test, y_test = x_test[-10:], y_test[-10:]

    model.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer="sgd",
        metrics=["accuracy"],
    )

    model.fit(
        x_train, y_train, validation_data=(x_validate, y_validate), batch_size=64, epochs=10
    )
    
    """scores = model.evaluate(x_test, y_test, verbose=0)
    print("Accuracy: %.2f%%" % (scores[1]*100))"""
    
    return model

def predict(gru, data):
    return gru.predict(data)

def save_GRU(gru, filename = 'GRU.pkl'):
    with open(filename, 'wb') as fid:
        pickle.dump(gru, fid)    

def load_GRU(filename = 'GRU.pkl'):
    with open(filename, 'rb') as fid:
        return pickle.load(fid)
    

if __name__ == "__main__":
    train_data = (np.random.randint(0, 900, size=(500, 500)), np.random.randint(0, 1, size=(500, 1)))
    test_data = (np.random.randint(0, 900, size=(500, 500)), np.random.randint(0, 1, size=(500, 1)))

    lstm = train_LSTM(train_data, test_data)