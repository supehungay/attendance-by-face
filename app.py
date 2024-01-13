import cv2
from apis  import add_faces
from apis.face_recognition import face_recognition, FaceRecognitionDataset
import firebase_admin
from firebase_admin import credentials, db, storage
from config import *
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
app = Flask(__name__)
dataset = None
attendances = None
sift_train = None
sift_test = None
model = None
def init_db():
    cred = credentials.Certificate(CERD)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DB_URL,
        'storageBucket': STR_URL
    })
    dataset = FaceRecognitionDataset()
    return cred, dataset

def get_data():
    data_ref = db.reference('Students')
    data = data_ref.get()
    if data is not None:
        print(data)
        data_list = [{'key': key, 'value': value} for key, value in data.items()]
        return data_list
    return None
    
    
@app.route('/')
def index():
    data_list = get_data()
    print(data_list)
    # print(data_list)
    if data_list is None:
        return render_template('index.html')

    return render_template('index.html', data_list=data_list)


@app.route('/submit', methods=['POST'])
def submit_form():
    msv = request.form.get('msv')
    ten = request.form.get('name')
    lop = request.form.get('class')

    print(msv, ten, lop)
    keyspoints, descriptors, msv = add_faces.add_info(msv, ten, lop, sift_train)
    if keyspoints is not None:
        dataset.addNewID(keyspoints, descriptors, msv)
    else:
        dataset.update()
    # dataset.train_model_knn()
    return redirect('/')

@app.route('/detect')
def recogni():
    face_recognition(dataset=dataset, attendances=attendances, sift=sift_test, model=model)
    return redirect('/')
    
@app.route('/export', methods=['POST'])
def export_to_excel():
    data_list = get_data()
    if data_list is None:
        return jsonify({'message': 'Data deleted successfully'})
    
    df = pd.DataFrame(columns=['MSV', 'Họ tên', 'Lớp', 'Điểm danh', 'Thời gian', 'Ghi chú'])
    
    for item in data_list:
        msv = item['key']
        ten = item['value']['Họ tên']
        lop = item['value']['Lớp']
        diemdanh = item['value']['Điểm danh']
        thoigian = item['value']['Thời gian']
        ghichu = item['value']['Ghi chú']
        temp_df = pd.DataFrame({
            'MSV': msv,
            'Họ tên': ten,
            'Lớp': lop,
            'Điểm danh': diemdanh,
            'Thời gian': thoigian,
            'Ghi chú': ghichu
        }, index=[0])
        df = pd.concat([df, temp_df], ignore_index=True)
    file_name = f'attention_{datetime.now().strftime("%d-%m-%Y")}.xlsx'
    save_path = os.path.join('../output/', file_name)

    df.to_excel(save_path, index=False)
    return send_file(save_path, as_attachment=True)

@app.route('/delete/<msv>', methods=['DELETE'])
def delete_data(msv):
    data_ref = db.reference('Students')

    data_ref.child(msv).delete()
    
    bucket = storage.bucket()
    blob = bucket.blob(f'desc_key/{msv}_keypoints.pkl')
    if blob.exists():
        blob.delete()
    else:
        print(f'desc_key/{msv}_keypoints.pkl dont exist')
    blob_img = bucket.blob(f'data/{msv}.pkl')

    if blob_img.exists():
        blob_img.delete()
    else:
        print(f'data/{msv}.pkl dont exist')
    # train_model_knn()
    dataset.remove(msv=msv)
    return jsonify({'message': 'Data deleted successfully'})

if __name__ == '__main__':
    sift_train = cv2.xfeatures2d.SIFT_create(contrastThreshold=0.02, edgeThreshold=20)
    sift_test = cv2.xfeatures2d.SIFT_create(contrastThreshold=0.01, edgeThreshold=10)
    attendances = []
    cred, dataset = init_db()
    # model = dataset.get_knn()
    app.run(debug=True)
