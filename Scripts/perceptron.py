import numpy as np
import pickle

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay


def train_MLP(train_data, test_data):
    train = train_data.iloc[:, :-1]
    train_labels = train_data.iloc[:, -1]
    test = test_data.iloc[:, :-1]
    test_labels = test_data.iloc[:, -1]

    mlp = MLPClassifier(hidden_layer_sizes = (10, 20), random_state=1, max_iter=300).fit(train, train_labels)
    pred = mlp.predict(test.loc[:,:])

    cm = confusion_matrix(test_labels, pred)
    cm = cm/len(pred)
    print(cm)

    print(f"Accuracy: {cm[0,0]+cm[1,1]}")

    cmdknn = ConfusionMatrixDisplay(cm)
    cmdknn.plot()
    
    return mlp

def save_MLP(mlp, filename = 'MLP.pkl'):
    with open(filename, 'wb') as fid:
        pickle.dump(mlp, fid)    

def load_MLP(filename = 'MLP.pkl'):
    with open(filename, 'rb') as fid:
        return pickle.load(fid)


