from flask import flash, redirect, request, render_template, url_for
import os
from werkzeug.utils import secure_filename
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(request, user_upload_folder, id, name, username, emailAddr):
    # Kiểm tra xem người dùng đã tải lên file chưa
    if 'file' not in request.files:
        flash('No file part')
        return None  # Trả về None nếu không có file

    file = request.files['file']

    # Kiểm tra nếu không chọn file
    if file.filename == '':
        flash('No selected file')
        return None  # Trả về None nếu không chọn file

    if file and allowed_file(file.filename):
        # Tạo tên file ngẫu nhiên cho ảnh người dùng
        extension = file.filename.rsplit('.', 1)[1].lower()  # Lấy phần mở rộng của file
        filename_user = str(uuid.uuid4()) + '.' + extension  # Tạo tên file ngẫu nhiên với phần mở rộng đúng

        # Lưu ảnh dùng chung /static/img/avatar.png
        static_img_folder = os.path.join('static', 'img')
        if not os.path.exists(static_img_folder):
            os.makedirs(static_img_folder)
        static_file_path = os.path.join(static_img_folder, 'avatar.png')
        file.save(static_file_path)  # Lưu file vào /static/img/avatar.png

        # Lưu file vào thư mục riêng của người dùng
        user_upload_path = os.path.join(user_upload_folder, str(id))
        if not os.path.exists(user_upload_path):
            os.makedirs(user_upload_path)
        user_file_path = os.path.join(user_upload_path, filename_user)
        file.save(user_file_path)  # Lưu bản riêng của người dùng với tên ngẫu nhiên

        # Đường dẫn trả về cho ảnh dùng chung (fixed path)
        profile_pic = '/img/avatar.png'  # Đường dẫn ảnh dùng chung

        flash('File uploaded successfully')
        print(profile_pic)
        return profile_pic  # Trả về đường dẫn ảnh dùng chung

    else:
        print("eror")
        flash('Invalid file format.')
        return None  # Trả về None nếu file không hợp lệ

