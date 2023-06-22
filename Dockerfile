FROM python:3.10-slim

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir numpy pandas psycopg2-binary schedule matplotlib scikit-learn pillow_heif gdown tqdm Pillow opencv-python tensorflow keras mtcnn Deprecated fire
# RUN pip install --no-cache-dir -r requirements.txt
COPY ./src ./src
