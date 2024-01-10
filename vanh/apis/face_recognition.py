import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
from apis import detect_face
from config import *
from apis.info_to_database import get_desc_from_storage
from apis.sift_decorater import *

def main1():
    cred = credentials.Certificate(CERD)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DB_URL,
        'storageBucket': STR_URL
    })

    file_model = f'model/model_knn.pkl'
    bucket = storage.bucket(STR_URL)
    blob = bucket.blob(file_model)
    data_as_byte = blob.download_as_bytes()
    knn = pickle.loads(data_as_byte)


    cap = cv2.VideoCapture(1) 
    template = cv2.imread(TEMPLATE, 0)

    while True:
        ret, frame = cap.read()

        flipped_frame = cv2.flip(frame, 0)
        top_left, bottom_right = detect_face.detect_face_with_template(flipped_frame, template)
        face_detect = np.copy(flipped_frame)
        
        if bottom_right is None:
            cv2.putText(face_detect, "get close to the camera", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        elif top_left[0] < 0 or top_left[1] < 0:
            cv2.putText(face_detect, "Move face to center", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        else:
            cv2.rectangle(face_detect, top_left, bottom_right, (0, 0, 255), 2)
            face_crop = flipped_frame[(top_left[1]) : (bottom_right[1]), (top_left[0]) : (bottom_right[0]), :]
            face_crop = cv2.resize(face_crop, (64, 64))
            face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            
            output = knn.predict(face_crop.flatten().reshape(1,-1))
            cv2.putText(face_detect, str(output), top_left, cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            
        # show frame
        cv2.imshow('Video1', face_detect)
        
        k = cv2.waitKey(1)

        if  k==ord('q'):
            break

def face_recognition():
    sift = cv2.xfeatures2d.SIFT_create(contrastThreshold=0.01, edgeThreshold=10)
    keypoints, descriptors, labels = get_desc_from_storage()

    cap = cv2.VideoCapture(0) 
    template = cv2.imread(TEMPLATE, 0)

    while True:
        ret, frame = cap.read()

        flipped_frame = cv2.flip(frame, 1)
        try:

            top_left, bottom_right = detect_face.detect_face_with_template(flipped_frame, template)
            face_detect = np.copy(flipped_frame)
            
            if bottom_right is None:
                cv2.putText(face_detect, "get close to the camera", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            elif top_left[0] < 0 or top_left[1] < 0:
                cv2.putText(face_detect, "Move face to center", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            else:
                cv2.rectangle(face_detect, top_left, bottom_right, (0, 0, 255), 2)
                face_crop = flipped_frame[(top_left[1]) : (bottom_right[1]), (top_left[0]) : (bottom_right[0]), :]
                face_crop = cv2.resize(face_crop, (IMAGE_SIZE, IMAGE_SIZE))
                face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                
                output = match_best_image(face_crop, train_descriptors=descriptors, train_keypoints=keypoints, class_labels=labels, sift=sift)
                cv2.putText(face_detect, str(output), top_left, cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            cv2.imshow('Video1', face_detect)
        except ValueError as e:
            # Handle the case when there are no contours
            print("Error:", e)
            print("No contours found.")
        # show frame
        # cv2.imshow('Video1', face_detect)
        
        k = cv2.waitKey(1)

        if  k==ord('q'):
            break