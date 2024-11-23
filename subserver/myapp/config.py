import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nhom7_p2v'
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or 
        'mysql+pymysql://root:123456%40a@localhost:3306/flask_chat'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
