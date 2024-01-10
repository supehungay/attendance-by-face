import firebase_admin
from firebase_admin import credentials, db, storage
import os
import cv2
import numpy as np
import pickle
from config import *
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from statistics import mode

def img2db(msv, faces_zip):
    fileName = f'data/{msv}.pkl'
    bucket = storage.bucket(STR_URL)
    blob = bucket.blob(fileName)
    blob.upload_from_string(faces_zip)


def info2db(msv, ten, lop):
    ref = db.reference('Students')
    data = {
        msv:
            {
                'Họ tên': ten,
                'Lớp': lop
            }
    }
    key, value = data.popitem()
    ref.child(key).set(value)
    
def train_model_knn():
    bucket = storage.bucket(STR_URL)
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
    
def key_des2db(msv, keys_desc_zip):
    if keys_desc_zip is None or len(keys_desc_zip) <= 0:
        return
    file_name = f'desc_key/{msv}_keypoints.pkl'
    bucket = storage.bucket(STR_URL)
    blob = bucket.blob(file_name)
    blob.upload_from_string(pickle.dumps(keys_desc_zip))
    print("Succesfully upload to dataframe")
def convert_to_dict(desc, keys, idx=0):
    if desc is None or keys is None:
        return
    keypoints_data = {
        'keypoints': [
            {
                'pt': kp.pt,
                'size': kp.size,
                'angle': kp.angle,
                'response': kp.response,
                'octave': kp.octave,
                'class_id': kp.class_id
            } for kp in keys
        ],
        'descriptors': desc
    }
    return keypoints_data

def get_desc_from_storage():
    bucket = storage.bucket(STR_URL)
    blobs = bucket.list_blobs(prefix='desc_key/')
    all_keypoints = []
    all_descriptors = []
    all_msv = []
    idx = 0
    try:
        for blob in blobs:
            print(f'Blob {idx}: ')
            file_contents = blob.download_as_bytes()
            keys_desc_zip = pickle.loads(file_contents)
            file_name = os.path.basename(blob.name)
            msv = os.path.splitext(file_name)[0]
            for row in keys_desc_zip:
                keypoints = row.get('keypoints', [])
                fixed_keypoints = np.array([cv2.KeyPoint(x=key['pt'][0], y=key['pt'][1], size=key['size'], angle=key['angle'], response=key['response'], octave=key['octave'], class_id=key['class_id']) for key in keypoints])
                descriptors = row.get('descriptors', [])
                all_msv.append(msv.split("_")[0])
                all_descriptors.append(descriptors)
                all_keypoints.append(fixed_keypoints)
            print(f"MSV: {msv.split('_')[0]}")
            idx += 1
    except Exception as e:
        print(f'Error downloading file: {e}')
        return None, None, None
    KEYPOINTS = np.array(all_keypoints)   
    DESCRIPTORS = np.array(all_descriptors) 
    LABELS = np.asarray(all_msv)
    # print(KEYPOINTS.shape)
    # print(DESCRIPTORS.shape)
    # print(LABELS.shape)
    # print(LABELS)

    return KEYPOINTS, DESCRIPTORS, LABELS