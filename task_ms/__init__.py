from flask import Flask

def create_app(config_name):
    app=Flask(__name__)
    app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/AudioConv'  ##app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ConvAudio.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'cloud2022'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
    UPLOAD_FOLDER = 'C:/java'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'wma', 'acc', 'ogg'}
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS']=ALLOWED_EXTENSIONS
    return app