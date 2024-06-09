# LSTM and CNN for sequence classification in the IMDB dataset
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers.recurrent import LSTM
from tensorflow.python.keras.layers import Dropout
from tensorflow.python.keras.layers import Embedding
from keras_preprocessing import sequence
import numpy as np
import pickle


def convert_to_sequence(mesures):
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
        pression.append(int(pression_data[i].valeur * 900))
        flexion.append(int(flexion_data[i].valeur * 900))
        x.append(int(inertie_data[i].X * 900))
        y.append(int(inertie_data[i].Y * 900))
        z.append(int(inertie_data[i].Z * 900))

    return np.ndarray([pression, flexion, x, y, z])

def train_LSTM(train_data, test_data): # train_data : ([[[],[]], [[],[]]] mesures, [] labels)
    model = Sequential()

    # Embedding layer
    model.add(
        Embedding(input_dim=2000,
                input_length = training_length,
                output_dim=100,
                weights=[embedding_matrix],
                trainable=False,
                mask_zero=True))

    # Masking layer for pre-trained embeddings
    model.add(Masking(mask_value=0.0))

    # Recurrent layer
    model.add(LSTM(64, return_sequences=False, 
                dropout=0.1, recurrent_dropout=0.1))

    # Fully connected layer
    model.add(Dense(64, activation='relu'))

    # Dropout for regularization
    model.add(Dropout(0.5))

    # Output layer
    model.add(Dense(num_words, activation='softmax'))

    # Compile the model
    model.compile(
        optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    return model

def predict(lstm : Sequential, data):
    return lstm.predict(data)

def save_MLP(mlp, filename = 'LSTM.pkl'):
    with open(filename, 'wb') as fid:
        pickle.dump(mlp, fid)    

def load_MLP(filename = 'LSTM.pkl'):
    with open(filename, 'rb') as fid:
        return pickle.load(fid)
    

if __name__ == "__main__":
    train_data = (np.random.randint(0, 900, size=(500, 500)), np.random.randint(0, 1, size=(500, 1)))
    test_data = (np.random.randint(0, 900, size=(500, 500)), np.random.randint(0, 1, size=(500, 1)))

    lstm = train_LSTM(train_data, test_data)