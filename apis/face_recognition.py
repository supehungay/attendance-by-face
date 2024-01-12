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
from datetime import datetime, timedelta

class FaceRecognitionDataset:
    def __init__(self) -> None:
        self.keypoints, self.descriptors, self.labels = get_desc_from_storage()
        self.bucket = storage.bucket(STR_URL)
    
    @staticmethod
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
        return KEYPOINTS, DESCRIPTORS, LABELS

    def update(self):
        print("Starting update")
        blobs = self.bucket.list_blobs(prefix='desc_key/')
        all_keypoints = self.keypoints.tolist()
        all_descriptors = self.descriptors.tolist()
        all_msv = self.labels.tolist()
        idx = 0
        try:
            for blob in blobs:
                file_name = os.path.basename(blob.name)
                msv = os.path.splitext(file_name)[0]
                msv = msv.split("_")[0]
                if msv in self.labels:
                    continue
                print(f'Blob {idx}: ')
                file_contents = blob.download_as_bytes()
                keys_desc_zip = pickle.loads(file_contents)
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
            return
        self.keypoints = np.array(all_keypoints)   
        self.descriptors = np.array(all_descriptors) 
        self.labels = np.asarray(all_msv)
    def remove(self, msv):
        idx = np.where(self.labels == msv)[0]
        self.descriptors = np.delete(self.descriptors, idx, axis=0)
        self.keypoints = np.delete(self.keypoints, idx, axis=0)
        self.labels = np.delete(self.labels, idx, axis=0)
    def get_data(self):
        return self.keypoints, self.descriptors, self.labels
    
def face_recognition(dataset: FaceRecognitionDataset = None):
    sift = cv2.xfeatures2d.SIFT_create(contrastThreshold=0.01, edgeThreshold=10)
    keypoints, descriptors, labels = dataset.get_data()

    cap = cv2.VideoCapture(0) 
    template = cv2.imread(TEMPLATE, 0)
    imgBackground=cv2.imread(BACKGROUND)
    time_start = datetime.now()
    
    attended = []
    while True:
        ret, frame = cap.read()
        key_attention = cv2.waitKey(1)

        if  key_attention==ord('q') or key_attention==ord('Q'):
            break
        
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
                
                if output in attended:
                    cv2.putText(face_detect, "Attended", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 255, 50), 1)
                    cv2.putText(face_detect, str(output), (top_left[0] + 45, top_left[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 255, 50), 1)
                    
                else:   
                    cv2.putText(face_detect, str(output), (top_left[0] + 45, top_left[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                
                if (key_attention == ord('x') or key_attention == ord('X')) and output not in attended:
                    attended.append(output)
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
        except ValueError as e:
            print("Error:", e)
            print("No contours found.")
            pass
        imgBackground[100:100 + 480, 70:70 + 640] = face_detect
        cv2.imshow('Video1', imgBackground)
    cap.release()
    cv2.destroyAllWindows()