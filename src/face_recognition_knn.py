# import firebase_admin
# from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime, timedelta
import detect_face

def recognition():
    # cred = credentials.Certificate("../serviceAccountKey.json")
    # firebase_admin.initialize_app(cred, {
    #     'databaseURL': 'https://attendance-by-face-default-rtdb.firebaseio.com/',
    #     'storageBucket': 'attendance-by-face.appspot.com'
    # })

    file_model = f'model/model_knn.pkl'
    bucket = storage.bucket('attendance-by-face.appspot.com')
    blob = bucket.blob(file_model)
    data_as_byte = blob.download_as_bytes()
    knn = pickle.loads(data_as_byte)


    cap = cv2.VideoCapture(0) 
    template = cv2.imread('../image/input/template2.png', 0)
    imgBackground=cv2.imread("../image/input/background.jpg")
    time_start = datetime.now()
    
    while True:
        ret, frame = cap.read()

        flipped_frame = cv2.flip(frame, 1)
        
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
            
            face_to_predict = face_crop.flatten().reshape(1,-1)
            output = knn.predict(face_to_predict)[0]
            # distances = knn.predict_proba(face_to_predict)
            # print(distances)
            cv2.putText(face_detect, str(output), top_left, cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            
            key_attention = cv2.waitKey(1)
            if key_attention == ord('x') or key_attention == ord('X'):
                ref = db.reference('Students')
                
                time_now = datetime.now()
                current_time = time_now.strftime("%d-%m-%Y %H:%M:%S")          
                threshold_time = timedelta(minutes=10)
                time_difference = time_now - time_start
                
                old_attendance = ref.child(output).child('Điểm danh').get()
                
                if time_difference > threshold_time:
                    ref.child(output).update({'Ghi chú': f'Muộn {round(time_difference.total_seconds() / 60, 2)} phút'})
                    new_attendance = "O" if old_attendance is None else old_attendance + " O"
                else:
                    new_attendance = "X" if old_attendance is None else old_attendance + " X"
                ref.child(output).update({'Điểm danh': new_attendance})
                ref.child(output).update({'Thời gian': current_time})
                
        # show frame
        imgBackground[100:100 + 480, 120:120 + 640] = face_detect
        cv2.imshow('Video1', imgBackground)
        
        key_beak = cv2.waitKey(1)

        if  key_beak==ord('q'):
            break

# recognition()
# with open('./data/20002053.pkl', 'rb') as w:
#     FACES=pickle.load(w)



