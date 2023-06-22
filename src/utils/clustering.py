from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
from utils.functions import logger
import numpy as np
import pandas as pd
import uuid


def find_best_eps(data):

    eps_min = 10.0  # Valore minimo di eps da esplorare.
    eps_max = 20.0  # Valore massimo di eps da esplorare.
    eps_step = 0.1  # Passo di incremento per eps.

    best_eps = None
    best_score = -1

    for eps in np.arange(eps_min, eps_max, eps_step):
        dbscan = DBSCAN(eps=eps, min_samples=4, metric='euclidean')
        dbscan.fit(data)
        labels = dbscan.labels_
        
        # Calcola il coefficiente di Silhouette per valutare la qualità del clustering.
        score = silhouette_score(data, labels)
        
        # Confronta il punteggio con il miglior punteggio finora.
        if score > best_score:
            best_score = score
            best_eps = eps


    return best_eps


def clusterFaces(faces : pd.DataFrame):

    data = faces["embedded"].to_list()
    eps = find_best_eps(data)
    logger("Il valore di eps è: " + str(eps))

    if eps is None:
        return pd.DataFrame()
    
    dbscan = DBSCAN(eps=eps, min_samples=2, metric='euclidean')
    dbscan.fit(data)
    labels = dbscan.labels_

    logger("Numero di cluster trovati: " + str(len(set(labels))))
    
    # merge dei cluster con le facce
    faces["clusterid"] = labels
    faces["eps"] = eps

    # remove outliers
    faces = faces[faces["clusterid"] != -1]
    
   # Convertiamo i classici valori di cluster in UUID 
    for label in labels:
        uuid_str = str(uuid.uuid4())
        faces.loc[faces["clusterid"] == label, "clusterid"] = uuid_str

    return faces




