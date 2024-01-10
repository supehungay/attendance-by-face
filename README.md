
## Thiết lập Firebase
### Tạo project
- Truy cập: [Fierbase](https://firebase.google.com/)
- Get Started
- create project: Attendance by face
- continue...
- create project

### Tạo realtime database:
build -> realtime database -> create database -> database option -> next -> Security rules (click chọn Start in test mode) -> enable

### Tạo storage (lưu trữ model và ảnh nén):
build -> storage -> get started -> click chọn Start in test mode -> next -> done

### Tạo private key
click icon cài đặt cạnh project overview -> project settings -> service accounts -> python -> generate new private key -> generate key -> download về project hiện tại -> đổi tên thành serviceAccountKey.json

## Mô tả file:
```sh
detect_face.py: xử lí phần da mặt đưa ra tọa độ khuân mặt
info_to_database.py: thực hiện thêm thông tin cá nhân vào realtime database; ảnh và model knn sau khi fit vào storage
add_faces.py: thêm khuôn mặt và thông tin cá nhân
face_recognition.py: phát hiện khuận mặt mới mã sinh viên tương ứng hiển thị
sift_decorater.py: chứa các phương thức tạo descriptor từ đặc trung trong phương pháp SIFT
```

## Hướng dẫn chạy code:
0. **Tạo database trên Fire theo hướng dẫn trên**

1. **Clone repository**
    Để setup local, bạn cần clone repository này về:
```shell
    git clone
```
2. **Tạo và khởi chạy môi trường ảo**
```shell
    python -m venv venv
```
Kích hoạt `venv`
```
venv/Scripts/activate
```
3. **Install các thư viện cần thiết**
```shell
pip install -r requirements.txt
```
4. **Cài đặt biến môi trường**
Bạn cần chỉnh sửa đường dẫn trong `set_env.ps1`
5. **Khởi chạy server**
```shell
    python .\app.py
```
