from flask import Flask, render_template, url_for, flash, redirect, request, send_file, send_from_directory, session, jsonify
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import os
from middlewares.loggin import check_session
from middlewares.file_upload import handle_file_upload
from sqlalchemy import func
import bcrypt
import uuid
import re
from werkzeug.utils import secure_filename
from urllib.parse import unquote, quote
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import SQLAlchemyError

# Khởi tạo các đối tượng cần thiết
db = SQLAlchemy()
socket = SocketIO()
cors = CORS()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    blog_posts = db.relationship('BlogPost', backref='author', lazy=True)
    chats1 = db.relationship('Chat', foreign_keys='Chat.userID1', backref='user1', lazy=True)
    chats2 = db.relationship('Chat', foreign_keys='Chat.userID2', backref='user2', lazy=True)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    userID = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    authorname = db.Column(db.String(100))
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    imagepath = db.Column(db.String(255))
    publish = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship('CommentBlog', backref='post', lazy=True)
    liked_blogs = db.relationship('LikedBlog', backref='blog', lazy=True)

class CommentBlog(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)  # Sử dụng id làm khóa ngoại
    username = db.Column(db.String(20))
    comment = db.Column(db.Text, nullable=False)

class Chat(db.Model):
    id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    userID1 = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    userID2 = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.String(36), db.ForeignKey('chat.id'), nullable=False)
    chat_messages = db.relationship('ChatMessage', backref='message', lazy=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    sender_username = db.Column(db.String(50), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('message.room_id'), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    myid = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    ischat = db.Column(db.Boolean, default=False)

class LikedBlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)  # Sử dụng id làm khóa ngoại
    userID = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    liked = db.Column(db.Boolean, default=True)

# Khởi tạo Flask app
app = Flask(__name__, static_folder='static')  # Chú ý đường dẫn đến thư mục assets

# Cấu hình
app.config['SECRET_KEY'] = 'secret-hhhh'
app.config['UPLOAD_FOLDER'] = 'static/users_uploads'
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'openu.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://vanphuc:123456#a@flask-mysql-server.mysql.database.azure.com:3306/flask_database'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456%40a@localhost/flask_mysql'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456%40a@localhost/flask_database'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo các thành phần
db.init_app(app)
socket.init_app(app, cors_allowed_origins="*")
cors.init_app(app)
bcrypt.init_app(app)

# Thêm thông báo mới vào bảng notification
@socket.on("add_stack_noti")
def add_notification(data):
    to_id = data["to"]
    from_id = data["from"]
    time = datetime.fromisoformat(data['timestamp'])  # Chuyển đổi timestamp sang đối tượng datetime
    content = data['message']

    try:
        # Tạo một thông báo mới
        notification = Notification(
            myid=to_id,
            content=content,
            timestamp=time,
            from_id=from_id,
            ischat=False
        )
        db.session.add(notification)
        db.session.commit()

    except Exception as e:
        print(f"Error adding notification: {str(e)}")

# Người dùng tham gia một phòng chat
@socket.on("join-chat")
def join_private_chat(data):
    room = data["rid"]
    myid = data['myid']
    join_room(room=room)

    try:
        # Lấy thông tin phòng chat
        chat = Chat.query.filter_by(id=room).first()
        if not chat:
            print(f"Chat room {room} not found.")
            return

        # Xác định người bạn trong phòng chat
        friend_id = chat.userID2 if chat.userID1 == myid else chat.userID1
        friend = User.query.filter_by(id=friend_id).first()
        if not friend:
            print(f"User {friend_id} not found.")
            return

        arr_data = {"username": friend.username, "room": room}
        socket.emit("joined-chat", arr_data, room=room)

    except Exception as e:
        print(f"Error joining chat room: {str(e)}")

# Xử lý sự kiện gửi tin nhắn
@socket.on("outgoing")
def chatting_event(json, methods=["GET", "POST"]):
    room_id = json["rid"]
    timestamp = datetime.fromisoformat(json["timestamp"])  # Chuyển đổi timestamp
    message = json["message"]
    sender_id = json["sender_id"]
    sender_username = json["sender_username"]

    try:
        # Lưu tin nhắn vào bảng ChatMessage
        chat_message = ChatMessage(
            content=message,
            timestamp=timestamp,
            sender_id=sender_id,
            sender_username=sender_username,
            room_id=room_id
        )
        db.session.add(chat_message)
        db.session.commit()

        # Kiểm tra và thêm thông báo nếu chưa tồn tại
        chat = Chat.query.filter_by(id=room_id).first()
        if not chat:
            print(f"Chat room {room_id} not found.")
            return

        recipient_id = chat.userID2 if chat.userID1 == sender_id else chat.userID1
        existing_notification = Notification.query.filter_by(myid=recipient_id, from_id=sender_id, ischat=True).first()

        if not existing_notification:
            notification = Notification(
                myid=recipient_id,
                content=message,
                timestamp=timestamp,
                from_id=sender_id,
                ischat=True
            )
            db.session.add(notification)
            db.session.commit()

    except Exception as e:
        print(f"Error handling outgoing message: {str(e)}")

    # Gửi tin nhắn tới các thành viên trong phòng
    socket.emit("message", json, room=room_id, include_self=False)

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    try:
        if request.method == "POST":
            email = request.form['email'].strip()
            username = request.form['username'].strip()
            password = request.form['password'].strip()

            # Kiểm tra nếu người dùng đã tồn tại
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                message = "User already exists"
            else:
                # Sinh ID và hash mật khẩu
                id = str(uuid.uuid4())

                # Sử dụng bcrypt để mã hóa mật khẩu
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

                # Tạo người dùng mới và lưu vào cơ sở dữ liệu
                new_user = User(id=id, username=username, email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()  # Lưu thay đổi vào DB

                # Tạo thư mục tải lên cho người dùng
                user_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], id)
                if not os.path.exists(user_upload_folder):
                    os.makedirs(user_upload_folder)

                message = "Registration successful"
                return redirect('/home')

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "You broke the server :(", 400

    return render_template("register.html", message=message)


# Login route -----------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            email = request.form['email'].strip()
            password = request.form['password'].strip()

            # Lấy thông tin người dùng từ DB
            user_info = User.query.filter_by(email=email).first()

            if user_info:
                # Kiểm tra mật khẩu
                if bcrypt.check_password_hash(user_info.password, password):
                    session['loggedin'] = True
                    session['id'] = user_info.id

                    return redirect('/home')   
                else:
                    return render_template('login.html', message="Wrong Email or Password")
            else:
                return render_template('login.html', message="Wrong Email or Password")
        return render_template("login.html")
    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "You broke the server :(", 400

# Home route ---------------------------------------------------------------------
@app.route("/")
@app.route("/home")
@check_session
def home():
    # Kiểm tra nếu ID tồn tại trong database
    id = session['id']
    user = User.query.get(id)
    if user:
        profile_pic = None

        # Lấy thông tin thông báo
        count_noti = Notification.query.filter_by(myid=id).count()
        count_noti_chat = Notification.query.filter_by(myid=id, ischat=1).count()

        # Lấy thông tin blog
        blog_info = BlogPost.query.filter_by(publish=1).order_by(func.random()).limit(5).all()
        user_info = user.username

        # Cài đặt ảnh đại diện
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], id)
        avatar_path_full = avatar_path + '/avatar.jpg'
        if os.path.exists(avatar_path_full):
            profile_pic = id + '/' + 'avatar.jpg'
        if profile_pic is None:
            profile_pic = os.path.join("", "../../img/avatar.jpg")

        data = []
        noti_list = Notification.query.filter_by(myid=id).all()
        for noti in noti_list:
            rid = Chat.query.filter(
                (Chat.userID1 == id) & (Chat.userID2 == noti.from_id) |
                (Chat.userID1 == noti.from_id) & (Chat.userID2 == id)
            ).first()

            sender = User.query.get(noti.from_id)
            sender_pic = None
            sender_ava_path = os.path.join(app.config['UPLOAD_FOLDER'], str(noti.from_id))
            sender_ava_full = sender_ava_path + '/avatar.jpg'
            if os.path.exists(sender_ava_full):
                sender_pic = str(noti.from_id) + '/avatar.jpg'
            if sender_pic is None:
                sender_pic = os.path.join("", "../../img/avatar.jpg")

            data.append({
                "myid": noti.myid,
                "fromid": noti.from_id,
                "fromname": sender.username,
                "content": noti.content,
                "time": noti.timestamp,
                "sender_pic": sender_pic,
                "ischat": noti.ischat,
                "rid": rid.id if rid else None
            })

        # Trả về trang index
        return render_template('index.html', blog_info=blog_info, user_info=user_info,
                               profile_pic=profile_pic, myid=id, data=data,
                               count_noti=count_noti, count_noti_chat=count_noti_chat)

    return redirect('/login')



# Profile route -----------------------------------------------
@app.route('/profile')
@check_session
def profile():
    id = session['id']
    user = User.query.get(id)
    if user:
        profile_pic = None
        blog_count = BlogPost.query.filter_by(userID=id).count()

        # Lấy thông tin người dùng và blog
        username = user.username
        blog_info = BlogPost.query.filter_by(userID=id).all()
        published_blogs = BlogPost.query.filter_by(userID=id, publish=1).all()

        # Lấy thông tin blog đã thích
        liked_blogs_title = BlogPost.query.join(LikedBlog).filter(LikedBlog.liked == 1, LikedBlog.userID == id).all()

        # Lấy thông tin về các blog đã thích
        total_blog = []
        for liked_blog in liked_blogs_title:
            total_blog.append(liked_blog)

        # Cài đặt ảnh đại diện
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], id)
        avatar_path_full = avatar_path + '/avatar.jpg'
        if os.path.exists(avatar_path_full):
            profile_pic = id + '/' + 'avatar.jpg'
        if profile_pic is None:
            profile_pic = os.path.join("", "../../img/avatar.jpg")

        # Trả về trang profile
        return render_template('profile.html'
                               ,username=username
                               ,blog_info=blog_info
                               ,profile_pic=profile_pic
                               ,published_blogs=published_blogs
                               ,liked_blogs=total_blog
                               ,blog_count=blog_count)

    return redirect('/login')



# Settings user information route -------------------------------
@app.route('/settings', methods=["GET", "POST"])
@check_session
def settings():
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại
    
    name = user.name
    username = user.username
    email = user.email
    hashed_password = user.password
    
    profile_pic = None

    user_upload_folder = app.config['UPLOAD_FOLDER']  # Thư mục chính của user uploads

    if request.method == "POST":
        # Cập nhật thông tin người dùng nếu có thay đổi
        if 'name' in request.form:
            new_name = request.form['name']
            user.name = new_name
            db.session.commit()
            name = new_name

        if 'username' in request.form:
            new_username = request.form['username']
            user.username = new_username
            db.session.commit()
            username = new_username

        if 'email' in request.form:
            new_email = request.form['email']
            user.email = new_email
            db.session.commit()
            email = new_email

        if 'password' in request.form:
            new_password = request.form['password']
            if new_password:
                if bcrypt.checkpw(new_password.encode('utf-8'), hashed_password):
                    print('Please provide a password different from your old one!')
                    return redirect(request.url)
                else:
                    new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    user.password = new_hashed_password
                    db.session.commit()
                    hashed_password = new_hashed_password
            else:
                pass

        # Xử lý ảnh đại diện nếu người dùng upload
        profile_pic = handle_file_upload(request, user_upload_folder, id, name, username, email)
        print(profile_pic)
        # if profile_pic is None:
        #     print(profile_pic)
        #     return redirect(request.url)  # Nếu không có file hợp lệ thì quay lại trang cài đặt

    # Kiểm tra xem ảnh đại diện có tồn tại không
    if profile_pic is None:
        profile_pic = 'img/avatar.png'  # Đường dẫn mặc định

    return render_template('settings.html', name=name, username=username, email=email, profile_pic=profile_pic)


# Logout route -----------------------------------------------
@app.route('/logout')
def logout():
    session.pop('loggedin')
    session.pop('id')
    return redirect('/login')


# Called to when create blog ----------------------------------
@app.route("/save_blog", methods=["GET", "POST"])
@check_session
def save_blog():
    id = session.get('id')
    user = User.query.get(id)

    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại

    username = user.username

    if request.method == "POST":
        try:
            blogTitle = request.json.get('blogTitle')
            blogContent = request.json.get('blogContent')

            if blogTitle and blogContent:
                new_blog = BlogPost(userID=id, title=blogTitle, content=blogContent, authorname=username)
                db.session.add(new_blog)
                db.session.commit()
                return "Blog successfully uploaded!"
            else:
                return "Blog title or content is missing.", 400
        except SQLAlchemyError as error:
            print(f"ERROR: {error}", flush=True)
            db.session.rollback()  # Rollback nếu có lỗi xảy ra
            return "You broke the server :(", 400

    return None
  
# Delete blog route
@app.route("/delete_blog", methods=["POST"])
@check_session
def delete_blog():
    id = session.get("id")
    user = User.query.get(id)

    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại
    
    try:
        # Lấy ID của blog cần xóa từ yêu cầu POST
        blog_id = request.form.get('blog_id')   
        blog = BlogPost.query.get(blog_id)

        if blog:
            if blog.userID != id:  # Kiểm tra quyền sở hữu blog
                return jsonify({"error": "You are not authorized to delete this blog"}), 403

            # Xóa các bản ghi liked_blog liên quan đến blog
            LikedBlog.query.filter_by(blog_post_id=blog_id).delete()

            # Xóa các bình luận liên quan đến blog
            CommentBlog.query.filter_by(blog_post_id=blog_id).delete()

            # Sau đó xóa blog
            db.session.delete(blog)
            db.session.commit()
        
        return redirect(url_for('profile'))

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "Internal Server Error", 500


# Route will be called when update publish or not
@app.route("/update_published", methods=["POST"])
@check_session
def published():
    id = session.get('id')
    user = User.query.get(id)

    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại

    try:
        blog_id = request.json.get('blogID')
        published = request.json.get('published')
        
        blog = BlogPost.query.get(blog_id)
        if blog:
            blog.publish = published
            db.session.commit()

        return 'Updated'

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "You broke the server :(", 400
        
#-----------------------------------------------------------------------------------------------   
#-------------------------------- Will look later -----------------------------------------------
# Routes to render out each individual blog when press on the title of a blog

@app.route('/blog/<string:blog_title>')
@check_session
def view_blog(blog_title):
    id = session.get('id')
    user = User.query.get(id)

    if not user:
        return redirect(url_for('login'))  # Nếu người dùng không tồn tại, chuyển hướng tới trang đăng nhập

    decode_title = unquote(blog_title)  # Giải mã tiêu đề blog

    # Lấy thông tin bài viết từ cơ sở dữ liệu
    blog_post = BlogPost.query.filter_by(title=decode_title, publish=1).first()

    if blog_post:
        # Lấy tất cả các bình luận liên quan đến bài viết này
        comments = CommentBlog.query.filter_by(blog_post_id=blog_post.id).all()
        liked = LikedBlog.query.filter_by(blog_post_id=blog_post.id, userID=id).first()

        liked = liked.liked if liked else 0  # Mặc định là 0 nếu người dùng chưa thích bài viết

        return render_template('blog.html', 
                               title=blog_post.title, 
                               content=blog_post.content, 
                               likes=blog_post.likes, 
                               comment_Content=comments, 
                               id=blog_post.userID, 
                               authorname=blog_post.authorname, 
                               liked=liked)
    else:
        # Nếu bài viết không tồn tại hoặc không có quyền truy cập, kiểm tra tác giả
        blog_post = BlogPost.query.filter_by(title=decode_title).first()

        if blog_post and blog_post.userID == id:
            comments = CommentBlog.query.filter_by(blog_post_id=blog_post.id).all()
            liked = LikedBlog.query.filter_by(blog_post_id=blog_post.id, userID=id).first()

            liked = liked.liked if liked else 0

            return render_template('blog.html', 
                                   title=blog_post.title, 
                                   content=blog_post.content, 
                                   likes=blog_post.likes, 
                                   comment_Content=comments, 
                                   id=blog_post.userID, 
                                   authorname=blog_post.authorname, 
                                   liked=liked)
        else:
            return redirect(url_for('home'))  # Chuyển hướng về trang chủ nếu không phải tác giả



#-----------------------------------------------------------------------------------------------   
#-----------------------------------------------------------------------------------------------   


# Routes for generating new chat by searching for users
from flask import jsonify

@app.route('/new_chat', methods=["POST"])
@check_session
def new_chat():
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại
    
    try:
        if request.method == "POST":
            search_input = request.form.get('search_input')
            
            # Kiểm tra đầu vào là email hay username
            if re.match(r'^[\w\.-]+@[\w\.-]+$', search_input):
                recipient = User.query.filter_by(email=search_input).first()
            else:
                recipient = User.query.filter_by(username=search_input).first()
                
            if recipient:
                recipient_id = recipient.id
                # Kiểm tra xem đã có cuộc trò chuyện giữa hai người chưa
                chat_exists = Chat.query.filter(
                    ((Chat.userID1 == id) & (Chat.userID2 == recipient_id)) | 
                    ((Chat.userID1 == recipient_id) & (Chat.userID2 == id))
                ).first()
                
                if chat_exists:
                    return jsonify({'error': 'Chat already exists'}), 400
                
                # Kiểm tra xem đã có lời mời chưa
                invite_input = request.form.get('invite_input')
                existing_invite = Notification.query.filter_by(myid=recipient_id, from_id=id).first()
                
                if existing_invite:
                    return jsonify({'error': 'You are already invited', 'chat_id': recipient_id, 'content': invite_input}), 404
                else:
                    # Tạo chat mới
                    chat_id = str(uuid.uuid4())
                    new_chat = Chat(id=chat_id, userID1=id, userID2=recipient_id)
                    db.session.add(new_chat)
                    db.session.commit()
                    
                    # Tạo room cho chat mới
                    chat_roomID = chat_id
                    new_message = Message(room_id=chat_roomID)
                    db.session.add(new_message)
                    db.session.commit()
                    
                    return jsonify({'success': 'New chat created successfully', 'chat_id': chat_id, 'content': invite_input}), 200
            else:
                return jsonify({'error': 'User not found'}), 404

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "Internal Server Error", 500
    
    
    
@app.route('/deletenoti', methods=["POST"])
@check_session
def deletenoti():
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại
    
    try:
        if request.method == "POST":
            data = request.data.decode('utf-8')  # Giải mã dữ liệu từ bytes sang chuỗi UTF-8
            data_dict = json.loads(data)  # Chuyển đổi chuỗi JSON thành dictionary
            
            fromid = data_dict.get('fromid')
            toid = data_dict.get('toid')

            recipient = User.query.get(toid)
            
            if recipient:
                # Xóa thông báo từ bảng Notification
                notification = Notification.query.filter_by(myid=id, from_id=fromid).first()
                
                if notification:
                    db.session.delete(notification)
                    db.session.commit()
                
                return jsonify({'success': 'Notification deleted successfully'}), 200
            else:
                return jsonify({'error': 'User not found'}), 404

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "Internal Server Error", 500
    

import json
@app.route('/accept', methods=["POST"])
@check_session
def accept():
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại
    
    try:
        if request.method == "POST":
            data = request.data.decode('utf-8')  # Giải mã dữ liệu từ bytes sang chuỗi UTF-8
            data_dict = json.loads(data)  # Chuyển đổi chuỗi JSON thành dictionary
            
            if 'data' in data_dict:
                senderid = data_dict['data']
                
                # Kiểm tra đầu vào là email hay user ID
                if re.match(r'^[\w\.-]+@[\w\.-]+$', senderid):
                    recipient = User.query.filter_by(email=senderid).first()
                else:
                    recipient = User.query.get(senderid)
                
                if recipient:
                    recipient_id = recipient.id
                    # Kiểm tra nếu chat đã tồn tại
                    chat_exists = Chat.query.filter(
                        ((Chat.userID1 == id) & (Chat.userID2 == recipient_id)) | 
                        ((Chat.userID1 == recipient_id) & (Chat.userID2 == id))
                    ).first()
                    
                    if chat_exists:
                        return jsonify({'error': 'Chat already exists'}), 400
                    else:
                        # Tạo chat mới
                        chat_id = str(uuid.uuid4())
                        new_chat = Chat(id=chat_id, userID1=id, userID2=recipient_id)
                        db.session.add(new_chat)
                        db.session.commit()
                        
                        # Tạo room cho chat mới
                        new_message = Message(room_id=chat_id)
                        db.session.add(new_message)
                        db.session.commit()
                        
                        # Xóa thông báo lời mời
                        Notification.query.filter_by(myid=id, from_id=senderid).delete()
                        db.session.commit()

                        return jsonify({'success': 'New chat created successfully', 'chatroom': chat_id}), 200
                else:
                    return jsonify({'error': 'User not found'}), 404

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "Internal Server Error", 500



# Routes for chat (tất cả việc chat hay render list chat và tìm kiếm người dùng ở đây)
@app.route('/chat/', methods=["GET", "POST"])
@check_session
def allChat():
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:  # Kiểm tra nếu người dùng không tồn tại
        return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu không tồn tại
    
    try:
        # Lấy room ID nếu người dùng nhấp vào một cuộc trò chuyện
        room_id = request.args.get("rid", None)
        
        # Lấy thông báo chưa đọc trong chat
        count_noti_chat = Notification.query.filter_by(myid=id, ischat=1).count()
        
        # Lấy danh sách tất cả các cuộc trò chuyện của người dùng
        chat_list = Chat.query.filter(
            (Chat.userID1 == id) | (Chat.userID2 == id)
        ).all()
        
        # Lấy số lượng thông báo chưa đọc
        count_noti = Notification.query.filter_by(myid=id).count()
        
        data = []
        messages = []
        
        # Lấy tên người dùng của người đang đăng nhập
        ownname = user.username
        
        des_id = None
        if chat_list:
            if room_id:
                chat = Chat.query.get(room_id)
                if chat:
                    # Lấy đối tác trò chuyện
                    if chat.userID1 == id:
                        des_id = chat.userID2
                    else:
                        des_id = chat.userID1
                        
            for chat in chat_list:
                chat_roomID = chat.id
                try:
                    # Lấy tin nhắn trong phòng chat
                    messages_th = Message.query.filter_by(room_id=chat_roomID).all()
                    
                    # Lấy tin nhắn cuối cùng trong chat
                    latest_message = Message.query.filter_by(room_id=chat_roomID).order_by(Message.timestamp.desc()).first()
                    
                    # Lấy tên bạn bè trong cuộc trò chuyện
                    friend_id = chat.userID1 if chat.userID2 == id else chat.userID2
                    friend = User.query.get(friend_id)
                    
                    if room_id == chat_roomID:
                        for message in messages_th:
                            messages.append({
                                "content": message.content,
                                "timestamp": message.timestamp,
                                "sender_username": message.sender_username,
                            })
                    
                    data.append({
                        "username": friend.username,
                        "room_id": chat_roomID,
                        "last_message": latest_message.content if latest_message else "No messages yet",
                    })
                    
                except Exception as e:
                    print(f"Error retrieving messages: {e}")

        # Cập nhật ảnh đại diện
        profile_pic = None
        avatar_path_full = os.path.join(app.config['UPLOAD_FOLDER'], str(id), 'avatar.jpg')
        if os.path.exists(avatar_path_full):
            profile_pic = f"{id}/avatar.jpg"
        else:
            profile_pic = "../../img/avatar.jpg"
        
        # Render chat box template
        return render_template('chatbox-code.html', room_id=room_id, data=data, messages=messages, ownname=ownname, profile_pic=profile_pic, count_noti=count_noti, des_id=des_id, count_noti_chat=count_noti_chat)
    
    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return "Internal Server Error", 500
    


# Route to update the likes
@app.route('/updateLike', methods=["POST"])
@check_session
def update_like():
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:
        return redirect(url_for('login'))  # Redirect to login if user not logged in

    try:
        post_title = request.form.get('post_title')
        action = request.form.get('action')

        # Determine like/unlike value
        like_unlike = 1 if action == "like" else 0

        # Get the blog post by title (assuming it's a unique identifier)
        blog_post = BlogPost.query.filter_by(title=post_title).first()

        if blog_post:
            # Check if the user has already liked the blog
            liked_blog = LikedBlog.query.filter_by(blog_post_id=blog_post.id, userID=id).first()

            if liked_blog:
                # Update like status
                liked_blog.liked = like_unlike
            else:
                # Insert a new like or unlike
                new_like = LikedBlog(blog_post_id=blog_post.id, userID=id, liked=like_unlike)
                db.session.add(new_like)
            
            db.session.commit()

            return jsonify({"message": "Likes updated successfully"}), 200
        else:
            return jsonify({"error": "Blog post not found"}), 404

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return jsonify({"error": "Internal Server Error"}), 500




# Routes to add comment to the database, which will be retrieve when viewing each blog
@app.route('/addComment/<string:blog_title>', methods=["POST"])
@check_session
def addComments(blog_title):
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    try:
        commentContent = request.form['content']
        
        if commentContent:
            # Get the blog post by title (assuming it's a unique identifier)
            blog_post = BlogPost.query.filter_by(title=blog_title).first()

            if blog_post:
                # Create and insert new comment into the database
                new_comment = CommentBlog(blog_post_id=blog_post.id, username=user.username, comment=commentContent)
                db.session.add(new_comment)
                db.session.commit()

                return "Comment added successfully", 200
            else:
                return "Blog post not found", 404  # Return error if blog post doesn't exist
        else:
            return "Comment can't be empty", 400

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return jsonify({"error": "Internal Server Error"}), 500





#Route to render about user information\
@app.route('/user/<string:user_id>', methods=["GET", "POST"])
@check_session
def viewProfile(user_id):
    id = session.get('id')
    user = User.query.get(id)
    
    if not user:
        return redirect(url_for('login'))  # Redirect to login if user not logged in
    
    decoded_id = unquote(user_id)
    print(decoded_id)

    try:
        # Retrieve user information
        user_info = User.query.get(decoded_id)
        if user_info:
            name = user_info.name
            username = user_info.username
            email = user_info.email

            # Retrieve all blogs that are published by the user
            all_blogs = BlogPost.query.filter_by(userID=decoded_id, publish=1).all()

            if not all_blogs:
                return "lmao"
            else:
                return render_template("userProfile.html", all_blogs=all_blogs, name=name, username=username, email=email)
        
        else:
            return "No user found!!", 400

    except Exception as error:
        print(f"ERROR: {error}", flush=True)
        return jsonify({"error": "Internal Server Error"}), 500


from datetime import datetime

@app.template_filter("ftime")
def ftime(date):
    # Kiểm tra nếu date là chuỗi hoặc đối tượng có thể chuyển thành timestamp
    if isinstance(date, str):
        try:
            # Cố gắng chuyển đổi chuỗi thành thời gian nếu có thể
            dt = datetime.fromtimestamp(int(date))
        except (ValueError, TypeError):
            return date  # Nếu không thể chuyển đổi thì trả về chuỗi nguyên thủy
    elif isinstance(date, int):  # Kiểm tra nếu là timestamp
        dt = datetime.fromtimestamp(date)
    elif isinstance(date, datetime):  # Nếu đã là đối tượng datetime
        dt = date
    else:
        return date  # Nếu kiểu dữ liệu không hợp lệ, trả về chuỗi nguyên thủy

    # Định dạng thời gian với giờ và phút theo định dạng 12 giờ (AM/PM)
    time_format = "%I:%M %p"  # %I là định dạng giờ 12h, %M là phút, %p là AM/PM
    formatted_time = dt.strftime(time_format)

    # Thêm ngày tháng vào chuỗi thời gian
    formatted_time += " | " + dt.strftime("%m/%d")
    
    return formatted_time


# Chạy ứng dụng Flask với SocketIO
if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        db.create_all()  # Tạo các bảng nếu chưa tồn tại
    socket.run(app, allow_unsafe_werkzeug=False, debug=True)