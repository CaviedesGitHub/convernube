#from task_ms import create_app
from flask_restful import Api

#from .vistas import VistaConversion, VistaTarea, VistaArchivo
#from .modelos import db
from flask_jwt_extended import JWTManager

#flask_app=create_app('default')
from flask import Flask
flask_app=Flask(__name__)
flask_app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@35.222.204.216:5432/postgres'  ##app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ConvAudio.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
flask_app.config['JWT_SECRET_KEY'] = 'cloud2022'
flask_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
UPLOAD_FOLDER = 'C:/java'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'wma', 'acc', 'ogg'}
flask_app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
flask_app.config['ALLOWED_EXTENSIONS']=ALLOWED_EXTENSIONS

app_context=flask_app.app_context()
app_context.push()


import enum
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.sql import func

db = SQLAlchemy()

from google.cloud.storage import Blob
from google.cloud import storag

client = storage.Client(project='neural-theory-367121')
bucket = client.get_bucket('bucketconversionaudio')

class ExtSound(enum.Enum):
    MP3 = 1
    ACC = 2
    OGG = 3
    WAV = 4
    WMA = 5
    
class EstadoTarea(enum.Enum):
    UPLOADED = 1
    PROCESSED = 2

class Tarea(db.Model):
    __tablename__ = 'tarea'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(DateTime(timezone=True), nullable=False, default=func.now())
    id_usr = db.Column(db.Integer, nullable=False)
    nom_arch = db.Column(db.Unicode(128))
    ext_conv = db.Column(db.Enum(ExtSound))
    estado = db.Column(db.Enum(EstadoTarea), default=EstadoTarea.UPLOADED)
    is_lock = db.Column(db.Boolean, default=False)
    
class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        else:
            return {'llave':value.name, 'valor':value.value}
    
class TareaSchema(SQLAlchemyAutoSchema):
    ext_conv=EnumADiccionario(attribute=('ext_conv'))
    estado=EnumADiccionario(attribute=('estado'))
    class Meta:
        model = Tarea
        include_relationships = True
        load_instance = True



db.init_app(flask_app)
db.create_all()





from flask_restful import Resource
from flask import request, session, send_file
#from task_ms.app import flask_app
from werkzeug.utils import secure_filename
import os
#from ..modelos import db, Tarea, TareaSchema, ExtSound, EstadoTarea
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError
from functools import wraps
from jwt import InvalidSignatureError
from datetime import datetime
import shutil

tarea_schema = TareaSchema()
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'wma', 'acc', 'ogg', 'MP3', 'WAV', 'WMA', 'ACC', 'OGG'}

def authorization_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()     
                lstTokens=request.path.split(sep='/')    
                lstTokens[len(lstTokens)-1]
                ##user_url=request.path[-1:]  ##generalizar a un numero de dos y mas cifras
                user_url=lstTokens[len(lstTokens)-1]
                user_jwt=str(int(get_jwt_identity()))
                if user_jwt==user_url:
                    return fn(*args, **kwargs)
                else:
                    return "Ataque Detectado"
            except InvalidSignatureError:
                return "Signature verification failed"
            except NoAuthorizationError:
                return "Missing JWT"
            except Exception as inst:
                print(type(inst))    # the exception instance
                return "Usuario Desautorizado"
        return decorator
    return wrapper

class VistaConversion(Resource):    
    @jwt_required()
    def delete(self):
        print("Inicio")
        return {"msg":"Crear Tarea."}

    @jwt_required()
    def post(self):
        print("Inicio")

        #print(request.form.get('tipo'))
        #if request.form.get('tipo') not in ALLOWED_EXTENSIONS:
        #   return {"msg":"Extensión Objetivo NO Valido."}
        
        if 'archivo' in request.files:
           print("Archivo")
           file = request.files['archivo']
           print("files")
           if file.filename != '':
              if file: #and allowed_file(file.filename):
                 user_jwt=int(get_jwt_identity())                
                 filename = secure_filename(file.filename)              
                 tipoExt=request.form.get('tipo')
                 if tipoExt is None:
                    tipoExt='OGG'
                 nueva_tarea = Tarea(id_usr=user_jwt, nom_arch=filename, ext_conv=ExtSound[tipoExt])                   
                 db.session.add(nueva_tarea)
                 db.session.commit()
                 nombre2=nombre_input(filename, nueva_tarea.id)      
                 print(nombre2)              
                 try:
                    file.save(nombre2)
                    temp=filename
                    temp=temp.replace('.', '-'+str(id)+'.')
                    blob = Blob('/entrada/'+temp, bucket)
                    cadext=os.path.splitext(temp)[1]
                    blob.upload_from_filename(nombre2,'audio/'+cadext[-3:])
                    blob.make_public()
                    if os.path.exists(nombre2):
                       os.remove(nombre2)
                 except Exception as inst:
                    print(inst.args)
                    db.session.delete(nueva_tarea)
                    db.session.commit()
                    return {"msg":"Error subiendo archivo. Tarea NO Creada."}            
                 print("NORMAL")
                 return tarea_schema.dump(nueva_tarea)
        print("NO VALIDO")
        return {"msg":"Archivo NO Valido."}

    @jwt_required()     
    def get(self):
        user_jwt=int(get_jwt_identity())  
        max=request.json.get("max", 50)
        if request.get_json()['order']=="ASC":
           return  [tarea_schema.dump(tar) for tar in Tarea.query.filter(Tarea.id_usr==user_jwt).order_by(Tarea.fecha.asc()).paginate(page=1, per_page=max, error_out=False)] 
        else:
           return  [tarea_schema.dump(tar) for tar in Tarea.query.filter(Tarea.id_usr==user_jwt).order_by(Tarea.fecha.desc()).paginate(page=1, per_page=max, error_out=False)]  

class VistaTarea(Resource):
    @jwt_required()
    def get(self, id_task):
        #user_jwt=int(get_jwt_identity())
        tarea=Tarea.query.get_or_404(id_task)
        #if tarea.id_usr!=user_jwt:
        #   return  {"Msg":"Usuario desautorizado."}
        return tarea_schema.dump(tarea)

    @jwt_required()
    def put(self, id_task):
        user_jwt=int(get_jwt_identity())
        tarea=Tarea.query.with_for_update().get_or_404(id_task)
        if tarea.id_usr!=user_jwt:
           db.session.rollback()
           return  {"Msg":"Usuario desautorizado."}
        if tarea.estado==EstadoTarea.PROCESSED:
           temp=tarea.nom_arch 
           temp=temp.replace('.', '-'+str(id_task)+'.') 
           temp=os.path.splitext(temp)[0]+'.'+tarea.ext_conv.name.lower()
           blob = Blob('/salida/'+temp, bucket) 
           blob.delete
           nombre=nombre_output(tarea.nom_arch, tarea.id, tarea.ext_conv.name.lower())
           if os.path.exists(nombre):
              os.remove(nombre)
           print("borrar el archivo")
        tarea.ext_conv=ExtSound[request.get_json()['tipo']]
        tarea.estado=EstadoTarea.UPLOADED
        tarea.is_locked=False
        db.session.commit()
        #tarea=Tarea.query.with_for_update().get_or_404(id_task)
        return tarea_schema.dump(tarea)

    @jwt_required()
    def delete(self, id_task):
        user_jwt=int(get_jwt_identity())
        tarea=Tarea.query.get_or_404(id_task)
        if tarea.id_usr!=user_jwt:
           return  {"Msg":"Usuario desautorizado."}
        temp=tarea.nom_arch
        temp=temp.replace('.', '-'+str(id_task)+'.')
        blob=Blob('/entrada/'+temp, bucket)
        blob.delete
        nombre=nombre_input(tarea.nom_arch, tarea.id)
        if os.path.exists(nombre):
           os.remove(nombre)
        print("borrar el archivo Original")
        if tarea.estado==EstadoTarea.PROCESSED:
           temp=os.path.splitext(temp)[0]+'.'+tarea.ext_conv.name.lower()
           blob = Blob('/salida/'+temp, bucket)
           blob.delete 
           nombre=nombre_output(tarea.nom_arch, tarea.id, tarea.ext_conv.name.lower())
           if os.path.exists(nombre):
              os.remove(nombre)
           print("borrar el archivo Procesado")
        db.session.delete(tarea)
        db.session.commit()
        return "", 204

class VistaArchivo(Resource):
    @jwt_required()
    def get(self, id_task):
        user_jwt=int(get_jwt_identity())
        tarea=Tarea.query.get_or_404(id_task)
        if tarea.id_usr!=user_jwt:
           return  {"Msg":"Usuario desautorizado."}
        temp=tarea.nom_arch
        if request.get_json()['archivo']=="INPUT":
           temp=temp.replace('.', '-'+str(id_task)+'.')
           blob=Blob('/entrada/'+temp, bucket)
           nombre=nombre_input(tarea.nom_arch, tarea.id)
        else:
           temp=temp.replace('.', '-'+str(id_task)+'.')
           temp=os.path.splitext(temp)[0]+'.'+tarea.ext_conv.name.lower()
           blob = Blob('/salida/'+temp, bucket)
           nombre=nombre_output(tarea.nom_arch, tarea.id, tarea.ext_conv.name.lower())
    
        blob.download_to_filename(nombre)
        return send_file(nombre, as_attachment=True)
    

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def nombre_temp(nom, id):
   current_date = datetime.now()
   dt=int(current_date.strftime("%Y%m%d%H%M%S"))
   cad='-'+str(dt)+'-'+str(id)+'.'
   temp=nom
   temp=temp.replace('.', cad)
   temp=os.path.join('../archivos/input', temp)
   return temp

def nombre_input(nom, id):
   temp=nom
   temp=temp.replace('.', '-'+str(id)+'.')
   #temp='../archivos/'+'input/'+temp
   temp='/nfs/'+'entrada/'+temp
   return temp

def nombre_output(nom, id, ext):
   temp=nom
   temp=temp.replace('.', '-'+str(id)+'.')
   #temp='../archivos/'+'output/'+temp
   temp='/nfs/'+'salida/'+temp
   return temp


api=Api(flask_app)
api.add_resource(VistaConversion, '/api/tasks/')
api.add_resource(VistaTarea, '/api/tasks/<int:id_task>/')
api.add_resource(VistaArchivo, '/api/files/<int:id_task>/')

jwt = JWTManager(flask_app)
