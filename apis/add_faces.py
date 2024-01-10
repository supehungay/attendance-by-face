import cv2
from apis import detect_face
import numpy as np
import pickle
from apis.info_to_database import info2db, key_des2db, convert_to_dict, img2db
from apis.sift_decorater import sift_descriptor
from config import *
def add_info(msv, ten, lop):
    
    cap = cv2.VideoCapture(0) 
    sift= cv2.xfeatures2d.SIFT_create(contrastThreshold=0.01, edgeThreshold=10)
    template = cv2.imread(TEMPLATE, 0)

    size = 20
    faces_data = []
    keys_data = []
    desc_data = []
    count = 0
    record = True
    while record:
        ret, frame = cap.read()
        start = cv2.waitKey(1)
        if start == ord('q'):
            record = False
            cap.release()
            cv2.destroyAllWindows()
            break

        if start != ord('r'):
            try:
                flipped_frame = cv2.flip(frame, 1)
                top_left, bottom_right = detect_face.detect_face_with_template(flipped_frame, template)
                face_detect = np.copy(flipped_frame)
                if bottom_right is None:
                    cv2.putText(face_detect, "get close to the camera", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                elif top_left[0] < 0 or top_left[1] < 0:
                    cv2.putText(face_detect, "Move face to center", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                else:
                    cv2.rectangle(face_detect, top_left, bottom_right, (0, 0, 255), 2)
                    cv2.putText(face_detect, "Press R to start recording", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                    cv2.imshow('Video1', face_detect)
            except Exception as e:
                print(f'Error downloading file: {e}')
                continue
        else:
            break
     # save faces data
    if record:
        startRecording(cap, faces_data, size, sift, desc_data, keys_data, template, msv, count=count)
        faces_data = np.asarray(faces_data)
        faces_data = faces_data.reshape(size, -1)
    # read frame and show
    if len(faces_data) < size:
        print('Chưa đủ số lượng ảnh đầu vào')
        return

    keypoints_desc_zip = []
    for idx, keypoint, descriptor in zip(np.arange(len(keys_data)), keys_data,desc_data):
        temp_zip = convert_to_dict(desc=descriptor, keys=keypoint,idx=idx)
        keypoints_desc_zip.append(temp_zip)
    keypoints_desc_zip = np.array(keypoints_desc_zip)
    key_des2db(msv=msv, keys_desc_zip=keypoints_desc_zip)
    faces_zip = pickle.dumps(faces_data)
    
    img2db(msv, faces_zip)
    info2db(msv, ten, lop)
    print(faces_data)

def startRecording(cap, faces_data, size, sift, desc_data, keys_data, template, msv, count=0):
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame from the camera.")
            break
        flipped_frame = cv2.flip(frame, 1)

        top_left, bottom_right = detect_face.detect_face_with_template(flipped_frame, template)
        face_detect = np.copy(flipped_frame)
        cv2.putText(face_detect, f'{str(len(faces_data))} / {size}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        
        if bottom_right is None:
            cv2.putText(face_detect, "get close to the camera", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        elif top_left[0] < 0 or top_left[1] < 0:
            cv2.putText(face_detect, "Move face to center", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        else:
            cv2.rectangle(face_detect, top_left, bottom_right, (0, 0, 255), 2)
            face_crop = flipped_frame[(top_left[1]) : (bottom_right[1]), (top_left[0]) : (bottom_right[0]), :]
            face_crop = cv2.resize(face_crop, (IMAGE_SIZE, IMAGE_SIZE))
            face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            mask_img = detect_face.get_ycrcb_mask(flipped_frame)
            
            # add face to data
            if len(faces_data) <= size and count % 10 == 0:
                try:
                    keypoint, descriptor = sift_descriptor(face_crop, sift)
                    faces_data.append(face_crop)
                    # cv2.imwrite(f"D:\\dulieuD\\Program Language\\Computer_Vision\\FinalExam\\project_Attendance-by-face\\draft\\vanh\\draft_image\\{msv}_{count}.png", face_crop)
                    desc_data.append(descriptor)
                    keys_data.append(keypoint)
                except ValueError as e:
                    print(f"Error: {e}")
                    continue
            count+=1
            cv2.imshow('Video2', face_crop)
            cv2.imshow('Video3', mask_img[1])
            
        # show frame
        cv2.imshow('Video1', face_detect)
        k = cv2.waitKey(1)

        if  k==ord('q') or len(faces_data) == size:
            break

    cap.release()
    cv2.destroyAllWindows()