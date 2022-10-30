#from conv_ms import create_app
#from .flask_celery import make_celery
from celery.schedules import crontab
from datetime import datetime
#from .modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema, ExtSound, EstadoTarea
from sqlalchemy.exc import IntegrityError
import os
import shutil
#from flask_mail import Mail, Message 
from pydub import AudioSegment

#flask_app=create_app('default')
from flask import Flask
flask_app=Flask(__name__)
flask_app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/AudioConv' #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ConvAudio.db'    
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_context=flask_app.app_context()
app_context.push()


print(__name__)

# encoding: utf8
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.sql import func

db = SQLAlchemy()

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
#db.create_all()


#mail = Mail(flask_app)
#flask_app.config['MAIL_SERVER']='smtp.gmail.com'
#flask_app.config['MAIL_PORT'] = 465
#flask_app.config['MAIL_USERNAME'] = 'caviedes72@gmail.com'
#flask_app.config['MAIL_PASSWORD'] = ''
#flask_app.config['MAIL_USE_TLS'] = False
#flask_app.config['MAIL_USE_SSL'] = True
#mail = Mail(flask_app) 
#msg = Message( 
#                'Hello', 
#                sender ='caviedes72@gmail.com', 
#                recipients = ['reciever’luispadilla1250@gmail.com'] 
#               ) 
#msg.body = 'Hello Flask message sent from Flask-Mail'
#mail.send(msg) 

from celery import Celery

def make_celery(app):
    celery=Celery(__name__, broker='redis://localhost:6379/0')
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task=ContextTask
    return celery

celery_app=make_celery(flask_app)
celery_app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'conv_ms.app.convertir_archivos',
        'schedule': 60.0,
        'args': ('prueba', datetime.utcnow())
    },
}  #minute='*/1'  crontab(sec='*/1')
celery_app.conf.timezone = 'UTC'

@celery_app.task(name='conv_ms.app.convertir_archivos', bind=True, ignore_result=False)
def convertir_archivos(self, nom_arch, fecha):
    print("convertir_archivos")
    while True:
        tarea=Tarea.query.with_for_update().filter(Tarea.estado==EstadoTarea.UPLOADED, Tarea.is_lock==False).order_by(Tarea.fecha.asc()).first()
        if tarea is None:
            #db.session.rollback()   #?
            break
        try:
            tarea.is_lock=True
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            continue
            ####return 'Error al bloquear Tarea', 409
        ##usuario=Usuario.query.with_for_update().get(id_usuario)
        #nombre=tarea.nom_arch
        #nombre=nombre.replace('.', '-'+str(tarea.id)+'.')
        #shutil.copy(os.getcwd()+'/archivos/input/'+nombre, os.getcwd()+'/archivos/output/'+nombre)
        convArchivo(tarea.id, tarea.nom_arch, tarea.ext_conv.name.lower())
        tarea=Tarea.query.with_for_update().get(tarea.id)
        if tarea is not None:
            try:
                tarea.is_lock=False
                tarea.estado=EstadoTarea.PROCESSED
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                ####return 'Error procesando Conversión', 409
        ####else:
            #db.session.rollback()   #?  Borrar el archivo!!

    
def convArchivo(id, nombre, ext):
    nombre_in=nombre.replace('.', '-'+str(id)+'.')
    nombre_out=os.path.splitext(nombre_in)[0]+'.'+ext.lower()
    nombre_in=os.getcwd()+'/archivos/input/'+nombre_in
    nombre_out=os.getcwd()+'/archivos/output/'+nombre_out
    print(nombre_in)
    print(nombre_out)
    #extension = os.path.basename(nombre)
    try:
        if nombre.endswith('.wav'):
            print(".wav")
            song = AudioSegment.from_wav(nombre_in)
        elif nombre.endswith('.mp3'):
            print(".mp3")  
            song = AudioSegment.from_mp3(nombre_in)
        elif nombre.endswith('.ogg'):
            print(".ogg")
            song = AudioSegment.from_ogg(nombre_in)   

        print("Antes de exportar")
        print(ext.lower())
        song.export(nombre_out, format=ext.lower())
    except Exception as inst:
        shutil.copy(nombre_in, nombre_out)