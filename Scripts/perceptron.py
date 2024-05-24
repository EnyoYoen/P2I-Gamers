import numpy as np
import cPickle

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay


def train_MLP(train_data, test_data):
    data_size = len(train_data.index)
    test_size = len(test_data.index)

    # TODO: Finish
    train = train_data.loc[:]
    train_labels = train_data[:]
    test = test_data.loc[:]
    test_labels = test_data[:]

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
        cPickle.dump(mlp, fid)    

def load_MLP(filename = 'MLP.pkl'):
    with open(filename, 'rb') as fid:
        return cPickle.load(fid)


