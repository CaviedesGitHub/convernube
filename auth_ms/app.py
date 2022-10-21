#from auth_ms import create_app
from flask_restful import Api
#from .vistas import VistaUsuario, VistaLogIn, VistaSignIn
#import vistas
from flask_jwt_extended import JWTManager
#from .modelos import db
#import modelos
from flask_login import current_user, LoginManager


from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_login import (current_user, login_user, logout_user, login_required)
#from auth_ms.modelos import db, Usuario, UsuarioSchema
#import auth_ms.modelos.modelos




# encoding: utf8
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


from flask import Flask
app=Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/AudioConv'  ##app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ConvAudio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'cloud2022'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
#app=create_app('default')
app_context=app.app_context()
app_context.push()


class Gender(enum.Enum):
    # as per ISO 5218
    not_known = '0'
    male = '1'
    female = '2'
    not_applicable = '9'


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    name = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    is_anonymous = False

    def __init__(self, *args, **kw):
        super(Usuario, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id
    
class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

usuario_schema = UsuarioSchema()


db.init_app(app)
db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)


class VistaSignIn(Resource):   
    def post(self):
        print('VistaSignIn')
        if request.json['password']==request.json['password2']:
            usuario=Usuario.query.filter(Usuario.email == request.json["email"]).first()
            if usuario is None:
                print(request.json["is_admin"])
                nuevo_usuario = Usuario(name=request.json["name"], email=request.json["email"], is_admin=eval(request.json["is_admin"]))
                nuevo_usuario.set_password(request.json["password"])
                db.session.add(nuevo_usuario)
                db.session.commit()
                token_de_acceso = create_access_token(identity=nuevo_usuario.id)
                return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id}
            else:
                return {"mensaje": "Usuario Ya Existe"}
        else:
            return {"mensaje": "No coincide password de confirmación"}

class VistaLogIn(Resource):
    def post(self):
        usuario = Usuario.query.filter(Usuario.email == request.json["email"]).first()
        db.session.commit()
        if usuario is not None and usuario.authenticate(request.json["password"]):
            login_user(usuario)
            token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso}
        else:
            return {"mensaje":"LogIn Incorrecto."}, 404
        
class VistaUsuario(Resource):   
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        return usuario_schema.dump(usuario)

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        if request.json.get("password") is not None:
           usuario.set_password(request.json["password"])
        usuario.name=request.json.get("name", usuario.name)
        usuario.email=request.json.get("email", usuario.email)
        if request.json.get("is_admin") is not None:
           usuario.is_admin=eval(request.json.get("is_admin"))
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return "Usuario Borrado.",  204


api = Api(app)
api.add_resource(VistaSignIn, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')
            

jwt = JWTManager(app)



