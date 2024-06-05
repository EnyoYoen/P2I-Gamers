import numpy as np
import pickle
import pandas as pd
from datetime import datetime
from tslearn.neural_network import TimeSeriesMLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

def convert_to_ts(mesures):
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

    df = pd.DataFrame({'date': date, 'pression': pression, 'flexion': flexion, 'x': x, 'y': y, 'z': z})
    df['date'] = pd.to_datetime(df['date'])
    time_series = df.set_index('date')
    print(time_series)
    return time_series

def train_MLP(train_data, test_data):
    train = train_data.iloc[:, :-1]
    train_labels = train_data.iloc[:, -1]
    test = test_data.iloc[:, :-1]
    test_labels = test_data.iloc[:, -1]

    mlp = TimeSeriesMLPClassifier(hidden_layer_sizes = (10, 20), random_state=1, max_iter=300).fit(train, train_labels)
    pred = mlp.predict(test.loc[:,:])

    cm = confusion_matrix(test_labels, pred)
    cm = cm/len(pred)
    print(cm)

    print(f"Accuracy: {cm[0,0]+cm[1,1]}")

    cmdknn = ConfusionMatrixDisplay(cm)
    cmdknn.plot()
    
    return mlp

def predict(mlp, data):
    return mlp.predict(data)

def save_MLP(mlp, filename = 'MLP.pkl'):
    with open(filename, 'wb') as fid:
        pickle.dump(mlp, fid)    

def load_MLP(filename = 'MLP.pkl'):
    with open(filename, 'rb') as fid:
        return pickle.load(fid)