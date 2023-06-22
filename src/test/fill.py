import psycopg2 as pg
import os
import uuid
from rich.console import Console
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

console = Console()

"""
    This file is used to fill the database with images
    The images are in the folder src/data
    The images are uploaded to the database in the table image

"""


database = "./src/data"

def upload_Image(path):

    conn = None
    name = path.split("/")[-1]
    name = name.split(".")[0]

    try:

        cloudinary.config( 
            cloud_name = "dkfufjo9o", 
            api_key = "164647762496236", 
            api_secret = "7-i96BfLItBw58yNfSY74dI95o0" 
        )

        conn = pg.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cur = conn.cursor()        
        uuids = uuid.uuid4()
        uuids = str(uuids)
        
        cloudinary.uploader.upload(path, public_id = name, folder = "reface", resource_type="image")
        cur.execute("INSERT INTO image (id,path) VALUES (%s,%s)", (uuids,name,))
        conn.commit()

    except (Exception, pg.DatabaseError) as error:  
        print(error)
    
    finally:
        if conn is not None:
            conn.close()



def upload_Images():

    for image in os.listdir(database):
        if image.endswith(".jpg"):
            # remove .jpg from the name
            upload_Image(os.path.join(database, image))


if __name__ == '__main__':
    upload_Images()
    console.print("[bold green]Data Uploaded[/bold green]")
