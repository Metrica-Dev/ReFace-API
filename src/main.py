import pandas as pd
from utils.functions import logger, get_images,get_faces_clustered , new_face, complete_image , get_faces , update_cluster_db ,get_clusters , new_cluster , define_cluster
from utils.clustering import clusterFaces
from sklearn.neighbors import NearestNeighbors
from model.Facenet512 import loadModel
import cloudinary
import cloudinary.uploader
import cloudinary.api

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=16)
from deepface import DeepFace
import os

weights = "src/weights/facenet512_weights.h5"
backends = "mtcnn"
target_size = (160, 160)
database = "src/data/"
model = loadModel(weights_path=weights)


def update_cluster():

    clusters = get_clusters()
    logger("We have " + str(clusters.shape[0]) + " clusters to update")
    faces = get_faces_clustered()
    logger("We have " + str(faces.shape[0]) + " faces to use")

    if clusters.empty:
        logger("We don't have clusters")
        return

    for index, row in clusters.iterrows():
        mean = np.mean(faces[faces["clusterid"] == index]["embedded"].to_list(), axis=0, dtype=np.float64)    
        update_cluster_db(str(index),mean)
        logger("Updated cluster " + str(index))

    logger("Updated all the clusters")


def elaborate_data():

    cloudinary.config( 
        cloud_name = "dkfufjo9o", 
        api_key = "164647762496236", 
        api_secret = "7-i96BfLItBw58yNfSY74dI95o0" 
    )

    update_cluster()

    df : pd.DataFrame = get_images() 
    logger("We have " + str(df.shape[0]) + " images to elaborate")
    
    checked_images = 0
    
    for index, row in df.iterrows():

        try:
            path = cloudinary.api.resource("reface/"+row["path"])
            face_objs = DeepFace.extract_faces(path["url"], detector_backend = backends, target_size = target_size , verbose = False)

        except Exception as e:
            print(f"Error: {e}")
            checked_images += 1
            complete_image(str(index))
            continue

        for face in face_objs:
            user_face = face['face'] 
            user_face_expanded = np.expand_dims(user_face, axis=0)
            embedded = model.predict(user_face_expanded,verbose=0)[0].tolist()
            new_face(str(index), embedded)

        # ogni 10 immagini voglio scrivere in log il numero di immagini elaborate
        checked_images += 1
        complete_image(str(index))
        
        if checked_images % int(df.shape[0] / 10) == 0 or checked_images == df.shape[0] or checked_images == 1: 
            logger("Elaborated " + str(checked_images) + "/" + str(df.shape[0])  + " images")

    faces = get_faces()     

    logger("We have " + str(faces.shape[0]) + " faces to cluster")

    cluster_df = get_clusters()

    logger("We have " + str(cluster_df.shape[0]) + " clusters")

    if not cluster_df.empty: 

        logger("We have clusters, we are going to check if we can add some faces to them")

        embeddings = cluster_df["embedded"].to_list()
        clusters = cluster_df.index.to_list()

        nn_model = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(embeddings)
        
        for index, row in faces.iterrows():

            face = row["embedded"]
            face_expanded = np.expand_dims(face, axis=0)
            distances, indices = nn_model.kneighbors(face_expanded)

            if distances[0][0] < cluster_df.loc[clusters[indices[0][0]]]["eps"]:
                logger("The face is close to a cluster, we are going to add it")
                define_cluster(index, clusters[indices[0][0]])
                faces.drop(index, inplace=True)

    if faces.size <  100:
            logger("The face after the embedded search is not enough to cluster")
            return
        
    logger("We have " + str(faces.shape[0]) + " faces to cluster")

    clustered = clusterFaces(faces)

    logger("We have " + str(clustered.shape[0]) + " faces clustered")

    # get the unique clusterid
    clusterid = clustered["clusterid"].unique()

    for cluster in clusterid:
        # calculate the mean of all the faces in the cluster
        mean = np.mean(clustered[clustered["clusterid"] == cluster]["embedded"].to_list(), axis=0)      
        new_cluster(cluster, mean, clustered[clustered["clusterid"] == cluster]["eps"][0])

    logger("Elaboration completed")

    for index, row in clustered.iterrows():
        define_cluster(index, row["clusterid"])

    logger("Cluster defined")


def elaborate_data_whitout():

    faces = get_faces()     

    logger("We have " + str(faces.shape[0]) + " faces to cluster")

    cluster_df = get_clusters()

    logger("We have " + str(cluster_df.shape[0]) + " clusters")

    if not cluster_df.empty: 

        logger("We have clusters, we are going to check if we can add some faces to them")

        embeddings = cluster_df["embedded"].to_list()
        clusters = cluster_df.index.to_list()

        nn_model = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(embeddings)
        
        for index, row in faces.iterrows():

            face = row["embedded"]
            face_expanded = np.expand_dims(face, axis=0)
            distances, indices = nn_model.kneighbors(face_expanded)

            if distances[0][0] < cluster_df.loc[clusters[indices[0][0]]]["eps"]:
                logger("The face is close to a cluster, we are going to add it")
                faces.drop(index, inplace=True)
                new_cluster(clusters[indices[0][0]], face, cluster_df.loc[clusters[indices[0][0]]]["eps"])
                
    if faces.size <  50:
            logger("The face after the embedded search is not enough to cluster")
            return
        
    logger("We have " + str(faces.shape[0]) + " faces to cluster")

    clustered = clusterFaces(faces)

    logger("We have " + str(clustered.shape[0]) + " faces clustered")

    # get the unique clusterid
    clusterid = clustered["clusterid"].unique()

    for cluster in clusterid:
        # calculate the mean of all the faces in the cluster
        mean = np.mean(clustered[clustered["clusterid"] == cluster]["embedded"].to_list(), axis=0)      
        new_cluster(cluster, mean, clustered[clustered["clusterid"] == cluster]["eps"][0])

    logger("Elaboration completed")

    for index, row in clustered.iterrows():
        define_cluster(index, row["clusterid"])

    logger("Cluster defined")


if __name__ == "__main__":
    elaborate_data()