
## Tổng quan
<image src="https://i.imgur.com/jhUDRoq.png" alt="Web UI" width="600 px">

<image src="https://i.imgur.com/DKWZmMI.png" alt="Detect UI" width="600 px">

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

## Mô tả folder/file:

```sh
apis/
    detect_face.py: xử lí phần da mặt đưa ra tọa độ khuân mặt
    info_to_database.py: thực hiện thêm thông tin cá nhân vào realtime database; ảnh và model knn sau khi fit vào storage
    add_faces.py: thêm khuôn mặt và thông tin cá nhân
    face_recognition.py: phát hiện khuận mặt mới mã sinh viên tương ứng hiển thị
    sift_decorater.py: chứa các phương thức tạo descriptor từ đặc trung trong phương pháp SIFT

ouput/: lưu trữ file excel khi dùng chúc năng xuất

static/ và template/: chứa các file cho phần fontend

app.py: phần backend

config.py: set cấu hình, có thể cần phải sử đường dẫn nếu DB_URL và STR_URL có chút khác biệt khi tạo trên firebase

README.md: hướng dẫn sử dụng

requirements.txt: thư viện cần thiết đề chạy chương trình

serviceAccountKey.json: chứa private key khi tạo trên firebase

set_env.ps1: thiết lập các đường của chương trình
```

## Hướng dẫn chạy code:
0. **Tạo database trên Firebase theo hướng dẫn trên** 

1. **Clone repository hoặc sẵn trong file zip**
Để setup local, bạn cần clone repository này về (bỏ qua nếu đã có file zip source code):
```shell
    git clone -b sift https://github.com/supehungay/attendance-by-face.git
```
2. **Tạo và khởi chạy môi trường ảo**
```shell
    python -m venv venv
```

Kích hoạt `venv`

```shell
venv/Scripts/activate
```

3. **Install các thư viện cần thiết**
```shell
pip install -r requirements.txt
```

4. **Cài đặt biến môi trường** 
```shell
Bạn cần chỉnh sửa đường dẫn trong `set_env.ps1`
```

5. **Khởi chạy server**
```shell
    python .\app.py
```
