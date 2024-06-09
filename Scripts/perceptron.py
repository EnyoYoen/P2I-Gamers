import numpy as np
import pickle
import pandas as pd
from datetime import datetime
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

def convert_to_sequence(mesures):
    pression_data = mesures[0]
    flexion_data = mesures[1]
    inertie_data = mesures[2]

    if len(inertie_data) > 0:
        array = np.zeros((190 * 5, 1))

        start_time = inertie_data[0].dateCreation
        if start_time.second == 0:
            end_time = start_time.replace(minute=start_time.minute - 1, second=59)
        else:    
            end_time = start_time.replace(second=start_time.second - 1)
        seconds = 0
        count = 0
        pression_offset = 0
        flexion_offset = 0
        inertie_offset = 0
        mesures_per_second = 10
        i_s = 0

        for i in range(0, len(inertie_data), 3):
            time = inertie_data[i].dateCreation
            
            if time < end_time:
                if end_time.second == 0:
                    end_time = end_time.replace(minute=end_time.minute - 1, second=59)
                else:    
                    end_time = end_time.replace(second=end_time.second - 1)
                seconds += 1

            actual_pression_offset = pression_offset
            actual_flexion_offset = flexion_offset
            actual_inertie_offset = inertie_offset
            for j in range(5):
                if pression_data[i_s + j - actual_pression_offset].dateCreation != time:
                    pression_offset += 1
                else:
                    if seconds * 190 + count * 19 + j < 190 * 5 and i_s + j < len(pression_data):
                        array[seconds * 190 + count * 19 + j] = pression_data[i_s + j].valeur

                if flexion_data[i_s + j - actual_flexion_offset].dateCreation != time:
                    flexion_offset += 1
                else:
                    if seconds * 190 + count * 19 + j + 5 < 190 * 5 and i_s + j < len(flexion_data):
                        array[seconds * 190 + count * 19 + j + 5] = flexion_data[i_s + j].valeur

            for j in range(3):
                if inertie_data[i + j - actual_inertie_offset].dateCreation != time:
                    inertie_offset += 1
                else:
                    array[seconds * 190 + count * 19 + j + 10] = inertie_data[i + j].X
                    array[seconds * 190 + count * 19 + j + 13] = inertie_data[i + j].Y
                    array[seconds * 190 + count * 19 + j + 16] = inertie_data[i + j].Z

            i_s += 5
            count += 1
            if count == mesures_per_second:
                count = 0
                if end_time.second == 0:
                    end_time = end_time.replace(minute=end_time.minute - 1, second=59)
                else:    
                    end_time = end_time.replace(second=end_time.second - 1)

        return array
    else:
        return np.zeros((190 * 5, 1))

def train_MLP(data):
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=1)
    train = train_data.iloc[:,:-1]
    train_labels = train_data.iloc[:,-1:]
    test = test_data.iloc[:,:-1]
    test_labels = test_data.iloc[:,-1:]

    mlp = MLPClassifier(hidden_layer_sizes = (10, 20), random_state=1, max_iter=1000).fit(train, train_labels)
    pred = mlp.predict(test.loc[:,:])
    print(pred)

    cm = confusion_matrix(test_labels, pred, labels=[0, 1])
    cm = cm/len(pred)
    print(cm)

    print(f"Accuracy: {(cm[0,0]+cm[1,1])*100}%")

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

def get_mesure_list(idMvmt, db):
    mesures_simples = db.get_mesure_simple(idMvmt)
    mesures_vects = db.get_mesure_vect(idMvmt)

    pression = []
    flexion = []
    for mesure_simple in mesures_simples:
        if mesure_simple.idCapteur < 6:
            pression.append(mesure_simple)
        else:
            flexion.append(mesure_simple)

    return [pression, flexion, mesures_vects]

if __name__ == "__main__":
    from database import Database

    db = Database()
    labels = []
    mouvements_data = []

    mouvements = db.list_mouvements()
    for mouvement in mouvements:
        nom = mouvement.name
        if nom is not None and nom != "NON":
            labels.append(mouvement.name)
            mouvements_data.append(convert_to_sequence(get_mesure_list(mouvement.idMvt, db)).flatten())

    df = pd.DataFrame(mouvements_data)
    df['label'] = pd.Series(labels).factorize()[0]

    mlp = train_MLP(df)
    unique_labels = np.unique(labels)
    unique_factors = np.unique(pd.Series(labels).factorize()[0])
    factor_to_label = {}
    for i in range(len(unique_labels)):
        factor_to_label[unique_factors[i]] = unique_labels[i]
    save_MLP((mlp, factor_to_label))