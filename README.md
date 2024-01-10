
## Thiết lập Firebase
### Tạo project
- Truy cập: [Fierbase](https://firebase.google.com/)
- Get Started
- create project: Attendance by face
- continue...
- create project

### Tạo realtime database:
build -> realtime database -> create database -> database option -> next -> Security rules (click chọn Start in test mode) -> enable

### tạo storage (lưu trữ model và ảnh nén):
build -> storage -> get started -> click chọn Start in test mode -> next -> done

### tạo private key
click icon cài đặt cạnh project overview -> project settings -> service accounts -> python -> generate new private key -> generate key -> download về project hiện tại -> đổi tên thành serviceAccountKey.json

## mô tả một vài file:
```sh
detec_face.py: xử lí phần da mặt đưa ra tọa độ khuân mặt
info_to_database.py: thực hiện thêm thông tin cá nhân vào realtime database; ảnh và model knn sau khi fit vào storage
add_faces.py: thêm khuôn mặt và thông tin cá nhân
face_recognition_knn.py: phát hiện khuận mặt mới mã sinh viên tương ứng hiển thị
```

## run code:
```sh
chỉ cần chạy file:
add_faces.py: để thực hiện thêm thông tin 
face_recognition_knn.py: để phát hiện
```
