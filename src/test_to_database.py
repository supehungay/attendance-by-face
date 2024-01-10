import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendance-by-face-default-rtdb.firebaseio.com/',
    'storageBucket': 'attendance-by-face.appspot.com'
})

ref = db.reference('Students')

def info2db(msv, ten, lop):
    data = {
        '20002053':
            {
                'Họ tên': 'Đỗ Mạnh Hùng',
                'Lớp': 'K65A5'
            }
    }
    key, value = data.items()
    ref.child(key).set(value)

    # for key, value in data.items():
    #     ref.child(key).set(value)