from conv_ms import create_app
from .flask_celery import make_celery
from celery.schedules import crontab
from datetime import datetime
from .modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema, ExtSound, EstadoTarea
from sqlalchemy.exc import IntegrityError
import os
import shutil
#from flask_mail import Mail, Message 
from pydub import AudioSegment

flask_app=create_app('default')
app_context=flask_app.app_context()
app_context.push()

db.init_app(flask_app)
#db.create_all()

print(__name__)


#mail = Mail(flask_app)
#flask_app.config['MAIL_SERVER']='smtp.gmail.com'
#flask_app.config['MAIL_PORT'] = 465
#flask_app.config['MAIL_USERNAME'] = 'caviedes72@gmail.com'
#flask_app.config['MAIL_PASSWORD'] = 'HeartOfMeloon1'
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

celery_app=make_celery(flask_app)
celery_app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'conv_ms.app.convertir_archivos',
        'schedule': 1.0,
        'args': ('prueba', datetime.utcnow())
    },
}  #minute='*/1'  crontab(sec='*/1')
celery_app.conf.timezone = 'UTC'

@celery_app.task(name='conv_ms.app.convertir_archivos', bind=True, ignore_result=False)
def convertir_archivos(self, nom_arch, fecha):
    print("convertir_archivos")
    tarea=Tarea.query.with_for_update().filter(Tarea.estado==EstadoTarea.UPLOADED, Tarea.is_lock==False).order_by(Tarea.fecha.asc()).first()
    if tarea is None:
        #db.session.rollback()   #?
        return
    try:
        tarea.is_lock=True
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return 'Error al bloquear Tarea', 409
    ##usuario=Usuario.query.with_for_update().get(id_usuario)
    #nombre=tarea.nom_arch
    #nombre=nombre.replace('.', '-'+str(tarea.id)+'.')
    #shutil.copy(os.getcwd()+'/archivos/input/'+nombre, os.getcwd()+'/archivos/output/'+nombre)
    convArchivo(tarea.id, tarea.nom_arch, tarea.ext_conv.name.lower())
    tarea=Tarea.query.with_for_update().get(tarea.id)
    if tarea is None:
        #db.session.rollback()   #?  Borrar el archivo!!
        return
    try:
        tarea.is_lock=False
        tarea.estado=EstadoTarea.PROCESSED
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return 'Error procesando Conversión', 409
    

def convArchivo(id, nombre, ext):
    nombre_in=nombre.replace('.', '-'+str(id)+'.')
    nombre_out=os.path.splitext(nombre_in)[0]+'.'+ext.lower()
    nombre_in=os.getcwd()+'/archivos/input/'+nombre_in
    nombre_out=os.getcwd()+'/archivos/output/'+nombre_out
    print(nombre_in)
    print(nombre_out)
    #extension = os.path.basename(nombre)
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