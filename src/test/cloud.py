
# curl -X PUT "http://yourserver.com/owncloud/remote.php/webdav/file.zip" -F myfile=@"/Users/Javi/Downloads/file.zip"
import os
import owncloud

oc = owncloud.Client('http://localhost:8080/')
oc.login('admin', 'admin')



database = "./src/data"

def upload_Image(path,image):

    oc.put_file(f'Photos/{image}', path)

    link_info = oc.share_file_with_link(f'Photos/{image}')

    print("Here is your link: " + str(link_info.get_link()))


def upload_Images():

    for image in os.listdir(database):
        if image.endswith(".jpg"):
            upload_Image(os.path.join(database, image),image)
            break


if __name__ == '__main__':
    upload_Images()