from conv_ms import create_app
from .flask_celery import make_celery
from celery.schedules import crontab
from datetime import datetime
from .modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema, ExtSound, EstadoTarea
from sqlalchemy.exc import IntegrityError
import os
import shutil

flask_app=create_app('default')
app_context=flask_app.app_context()
app_context.push()

db.init_app(flask_app)
#db.create_all()

print(__name__)

celery_app=make_celery(flask_app)
celery_app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'conv_ms.app.convertir_archivos',
        'schedule': crontab(minute='*/1'),
        'args': ('prueba', datetime.utcnow())
    },
}
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
    #usuario=Usuario.query.with_for_update().get(id_usuario)
    print(os.curdir)
    print(os.getcwd())
    shutil.copy(os.getcwd()+'/archivos/input/'+tarea.nom_arch, os.getcwd()+'/archivos/output/'+tarea.nom_arch)
    print(tarea.nom_arch)
    with open('archivos_login','a+') as file:
        file.write('Convertir Archivos: Fecha: {} - Archivo: {}\n'.format(fecha, nom_arch))
    print(fecha)   
    

