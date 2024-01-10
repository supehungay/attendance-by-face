from apis  import add_faces
from apis.face_recognition import face_recognition
# from apis.info_to_database import train_model_knn
import firebase_admin
from firebase_admin import credentials, db, storage
from config import *
import pandas as pd
from datetime import datetime
import os
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
# from flask import redirect, url_for
app = Flask(__name__)
def init_db():
    cred = credentials.Certificate(CERD)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DB_URL,
        'storageBucket': STR_URL
    })
    return cred

def get_data():
    data_ref = db.reference('Students')
    data = data_ref.get()
    if data is not None:
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
    add_faces.add_info(msv, ten, lop)
    
    # return f"Submitted: msv - {msv}, Tên - {ten}, lớp - {lop}"
      # Cập nhật lại dữ liệu sau khi thêm thông tin mới
    # data_list = get_data()

    # return redirect(url_for('index', data_list=data_list))
    return redirect('/')
    # return render_template('index.html', data_list = data_list)

@app.route('/detect')
def recogni():
    face_recognition()
    return redirect('/')
    
@app.route('/export', methods=['POST'])
def export_to_excel():
    data_list = get_data()
    df = pd.DataFrame(columns=['MSV', 'Họ tên', 'Lớp', 'Điểm danh', 'Thời gian', 'Ghi chú'])
    
    for item in data_list:
        msv = item['key']
        ten = item['value']['Họ tên']
        lop = item['value']['Lớp']
        diemdanh = item['value']['Điểm danh']
        thoigian = item['value']['Thời gian']
        ghichu = item['value']['Ghi chú']
        
        df = df.append({
            'MSV': msv,
            'Họ tên': ten,
            'Lớp': lop,
            'Điểm danh': diemdanh,
            'Thời gian': thoigian,
            'Ghi chú': ghichu
        }, ignore_index=True)
        
    print("Print to excel")

@app.route('/delete/<msv>', methods=['DELETE'])
def delete_data(msv):
    data_ref = db.reference('Students')

    data_ref.child(msv).delete()
    
    bucket = storage.bucket()
    blob = bucket.blob(f'data/{msv}.pkl')
    if blob.exists():
        blob.delete()
    else:
        print(f"Blob 'data/20002029.pkl' does not exist.")
    # train_model_knn()
    return jsonify({'message': 'Data deleted successfully'})

if __name__ == '__main__':
    cred = init_db()
    app.run(debug=True)
