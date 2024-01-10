import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import os
import cv2
import numpy as np
import pickle

from sklearn.neighbors import KNeighborsClassifier

cred = credentials.Certificate("../serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendance-by-face-default-rtdb.firebaseio.com/',
    'storageBucket': 'attendance-by-face.appspot.com'
})

def img2db(msv, faces_zip):
    # folderPath = './data'
    fileName = f'data/{msv}.pkl'
    bucket = storage.bucket('attendance-by-face.appspot.com')
    blob = bucket.blob(fileName)
    blob.upload_from_string(faces_zip)


def info2db(msv, ten, lop):
    ref = db.reference('Students')
    data = {
        msv:
            {
                'Họ tên': ten,
                'Lớp': lop,
                'Điểm danh': '',
                'Thời gian': '',
                'Ghi chú': ''
            }
    }
    key, value = data.popitem()
    ref.child(key).set(value)
    
# info2db('20002053', 'HUng', 'k12376')    
def train_model_knn():
    bucket = storage.bucket('attendance-by-face.appspot.com')
    blobs = bucket.list_blobs(prefix='data/')
    all_faces = []
    all_msv = []
    for blob in blobs:
        data_as_bytes = blob.download_as_bytes()
        loaded_data = pickle.loads(data_as_bytes)
        file_name = os.path.basename(blob.name)
        msv = os.path.splitext(file_name)[0]
        
        all_msv.extend([msv] * len(loaded_data))
        all_faces.extend(loaded_data)
        
    FACES = np.asarray(all_faces)    
    LABELS = np.asarray(all_msv)
    print(FACES.shape)
    print(LABELS.shape)
    
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)
    save_model = pickle.dumps(knn)
    blob = bucket.blob('model/model_knn.pkl')
    blob.upload_from_string(save_model)
    