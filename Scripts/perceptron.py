import numpy as np
import pickle
import pandas as pd
from datetime import datetime
from tslearn.neural_network import TimeSeriesMLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

def convert_to_sequence(mesures):
    pression_data = mesures[0]
    flexion_data = mesures[1]
    inertie_data = mesures[2]

    array = np.zeros((190 * 5, 1), dtype=int)

    print(inertie_data[0].dateCreation)
    start_time = datetime.strptime(inertie_data[0].dateCreation, '%Y-%m-%d %H:%M:%S.%f')
    end_time = start_time.replace(second=start_time.second - 1)
    seconds = 0
    count = 0
    pression_offset = 0
    flexion_offset = 0
    inertie_offset = 0
    mesures_per_second = 10
    for i in range(len(inertie_data)):
        time_str = inertie_data[i].dateCreation
        time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
        
        if time < end_time:
            end_time = end_time.replace(second=end_time.second - 1)
            if count < mesures_per_second:
                for j in range(count, mesures_per_second):
                    for k in range(19):
                        array[seconds * 190 + j * 10 + k] = 0
            seconds += 1

        actual_pression_offset = pression_offset
        actual_flexion_offset = flexion_offset
        actual_inertie_offset = inertie_offset
        for j in range(5):
            if pression_data[i * 5 + j - actual_pression_offset].dateCreation != time_str:
                array[seconds * 190 + count * 19 + j] = 0
                pression_offset += 1
            else:
                array[seconds * 190 + count * 19 + j] = pression_data[i * 5 + j].valeur

            if flexion_data[i * 5 + j - actual_flexion_offset].dateCreation != time_str:
                array[seconds * 190 + count * 19 + j + 5] = 0
                flexion_offset += 1
            else:
                array[seconds * 190 + count * 19 + j + 5] = flexion_data[i * 5 + j].valeur

        for j in range(3):
            if inertie_data[i * 3 + j - actual_inertie_offset].dateCreation != time_str:
                array[seconds * 190 + count * 19 + j + 10] = 0
                array[seconds * 190 + count * 19 + j + 13] = 0
                array[seconds * 190 + count * 19 + j + 16] = 0
                inertie_offset += 1
            else:
                array[seconds * 190 + count * 19 + j + 10] = inertie_data[i * 3 + j].X
                array[seconds * 190 + count * 19 + j + 13] = inertie_data[i * 3 + j].Y
                array[seconds * 190 + count * 19 + j + 16] = inertie_data[i * 3 + j].Z

        count += 1
        if count == mesures_per_second:
            count = 0
            end_time = end_time.replace(second=end_time.second + 1)

    if count < mesures_per_second:
        for j in range(count, mesures_per_second):
            for k in range(19):
                array[seconds * 190 + j * 10 + k] = 0
        seconds += 1
    if seconds < 4:
        for i in range((4 - seconds) * 190):
            array[seconds * 190 + i] = 0

    return array

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
    
if __name__ == "__main__":
    from database import Database

    db = Database()
    
    mesures_simples = db.get_mesure_simple(307)
    mesures_vects = db.get_mesure_vect(307)

    pression = []
    flexion = []
    for mesure_simple in mesures_simples:
        if mesure_simple.idCapteur < 6:
            pression.append(mesure_simple)
        else:
            flexion.append(mesure_simple)

    print(convert_to_sequence([pression, flexion, mesures_vects]))