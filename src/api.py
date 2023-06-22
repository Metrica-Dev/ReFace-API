from model.Facenet512 import loadModel
from deepface import DeepFace
import numpy as np
import pandas as pd
from datetime import datetime
import psycopg2 as pg
import schedule
import time
import uuid
import cv2

from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

from PIL import Image
# Permette di aprire immagini HEIF
from pillow_heif import register_heif_opener
register_heif_opener()

database = "data/"
weights = "weights/facenet512_weights.h5"
backends = "mtcnn"
target_size = (160, 160)

model = loadModel(weights_path=weights)
print("FaceNet512 loaded")


def upload_data():

    conn = None

    try:
        conn = pg.connect(
            host="192.168.0.91",
            database="reface",
            user="postgres",
            password="postgres"
        )

        cur = conn.cursor()
        cur.execute("INSERT INTO cluster (id,name,embedded) VALUES (%s,%s,%s)", ("1","test","11"))
        conn.commit()

    except (Exception, pg.DatabaseError) as error:  
        with open("error.log", "a") as f:
            f.write(str(datetime.now()) + ": " + str(error) + "\n")
    
    finally:
        if conn is not None:
            conn.close()

    return

def get_images():

    conn = None

    try:

        conn = pg.connect(
            host="192.168.0.91",
            database="reface",
            user="postgres",
            password="postgres"
        )

        cur = conn.cursor()
        cur.execute("SELECT path FROM image WHERE analyzed = false")
        rows = cur.fetchall()

        return rows
    
    except (Exception, pg.DatabaseError) as error:
        with open("error.log", "a") as f:
            f.write(str(datetime.now()) + ": " + str(error) + "\n")

    finally:
        if conn is not None:
            conn.close()


def perform_clustering():
    
    # Carica le immagini da analizzare
    images = get_images()

    with open("log.txt", "a") as f:
        f.write("immagini" + str(images) + "\n")

    # Se non ci sono immagini da analizzare, esci
    if len(images) < 100:
        with open("log.txt", "a") as f:
            f.write(str(datetime.now()) + ": " + "No much images to analyze\n")

    pass    


# Definisci l'orario di esecuzione dello script
# esegui lo script ogni giorno alle 18:45
schedule.every().hour.at("35:00").do(perform_clustering)

with open("log.txt", "a") as f:
    f.write("Start\n")

# Ciclo di esecuzione dello scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
