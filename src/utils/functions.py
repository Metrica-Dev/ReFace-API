from dotenv import load_dotenv
import psycopg2 as pg2
import uuid
import os
import pandas as pd
from datetime import datetime
import numpy as np

load_dotenv()

def logger(msg: str):
    with open('log.txt', 'a') as f:
        f.write(str(datetime.now().strftime("%d %B %Y, %H:%M %p")) + ": " + msg + '\n')

def get_images():

    """
        La seguente funzione si occupa di recuperare le immagini da elaborare.
        
        :Passo:
            1. Effettuare la connessione al database
            2. Recuperare le immagini da elaborare
                :Database:
                    - id
                    - path
                    - checked
                    - Face [] (lista di facce)
    """

    conn = None

    try:

        conn = pg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cur = conn.cursor()
        cur.execute("SELECT * FROM image WHERE analized = false")
        images = cur.fetchall()

        df = pd.DataFrame(images,columns=["id","path","analized"])
        df.set_index("id",inplace=True)
        return df
    
    except Exception as e:
        logger(f"Error: {e}")
        return pd.DataFrame()

    finally:
        if conn is not None:
            conn.close()

def get_faces_clustered():

    conn = None

    try:
            
            conn = pg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
    
            cur = conn.cursor()
            cur.execute("SELECT * FROM face WHERE clusterid IS NOT NULL")
            faces = cur.fetchall()

            df = pd.DataFrame(faces,columns=["id","embedded","imageid","clusterid"])
            df.set_index("id",inplace=True)
            return df

    except Exception as e:
        logger(f"Error: {e}")
        return pd.DataFrame()
    
    finally:
        if conn is not None:
            conn.close()


def get_faces():

    conn = None

    try:
            
            conn = pg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
    
            cur = conn.cursor()
            cur.execute("SELECT * FROM face WHERE clusterid IS NULL")
            faces = cur.fetchall()

            df = pd.DataFrame(faces,columns=["id","embedded","imageid","clusterid"])
            df.set_index("id",inplace=True)
            return df

    except Exception as e:
        logger(f"Error: {e}")
        return pd.DataFrame()
    
    finally:
        if conn is not None:
            conn.close()

def get_clusters():
    
    conn = None

    try:
                    
            conn = pg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
    
            cur = conn.cursor()
            cur.execute("SELECT * FROM cluster")
            clusters = cur.fetchall()

            df = pd.DataFrame(clusters,columns=["id","name","embedded","eps"])
            df.set_index("id",inplace=True)
            return df
    
    except Exception as e:
        logger(f"Error: {e}")
        return pd.DataFrame()
    
    finally:
        if conn is not None:
            conn.close()

def new_face(image_id : str, embedded: list[float]):

    """
        La seguente funzione si occupa di inserire una nuova faccia nel database.
        
        :Passo:
            1. Effettuare la connessione al database
            2. Inserire la faccia
    """

    conn = None

    try:

        conn = pg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        uuids = uuid.uuid4()
        uuids = str(uuids)

        cur = conn.cursor()

        # insert the data in the face table
        cur.execute("INSERT INTO face (id, imageid, embedded) VALUES (%s, %s, %s)", (uuids, image_id, embedded))
    
        conn.commit()

        
    
    except Exception as e:
        print(f"Error: {e}")
        return False

    finally:
        if conn is not None:
            conn.close()
    
    return True

def new_cluster(clusterid : str , embedded: list[float], eps: float):

    conn = None

    try:
            embedded = list(embedded)
            conn = pg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
    
            cur = conn.cursor()
    
            # insert the data in the face table
            cur.execute("INSERT INTO cluster (id, embedded, eps) VALUES (%s, %s, %s)", (clusterid, embedded, eps))
        
            conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:

        if conn is not None:
            conn.close()

def complete_image(image_id : str):

    conn = None

    try:

        conn = pg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cur = conn.cursor()
        cur.execute("UPDATE image SET analized = true WHERE id = %s", (image_id,))
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        if conn is not None:
            conn.close()

def update_cluster_db(clusterid : str, embedded: np.ndarray):

    conn = None

    try:

        conn = pg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cur = conn.cursor()
        cur.execute("UPDATE cluster SET embedded = %s WHERE id = %s", (embedded.tolist(), clusterid))
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        if conn is not None:
            conn.close()


def define_cluster(image_id, clusterid : str):

    conn = None

    try:
            
            conn = pg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
    
            cur = conn.cursor()
            cur.execute("UPDATE face SET clusterid = %s WHERE id = %s", (clusterid, image_id))
            conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        return False

    finally:
        if conn is not None:
            conn.close()
            

    pass