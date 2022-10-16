from flask_restful import Resource
from flask import request
#from task_ms.app import flask_app
from werkzeug.utils import secure_filename
import os
from ..modelos import db, Tarea, TareaSchema, ExtSound, EstadoTarea
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

class VistaTareas(Resource):
    @authorization_required()
    def post(self, id_usuario):
        #if request.form.get('tipo') not in ALLOWED_EXTENSIONS:
        #   return {"msg":"Extensión Objetivo NO Valido."}
        if 'archivo' in request.files:
           file = request.files['archivo']
           if file.filename != '':
              if file: #and allowed_file(file.filename):
                 filename = secure_filename(file.filename)              
                 nueva_tarea = Tarea(id_usr=id_usuario, nom_arch=filename, ext_conv=ExtSound[request.form.get('tipo')])                   
                 db.session.add(nueva_tarea)
                 db.session.commit()
                 nombre2=nombre_def(filename, nueva_tarea.id)                    
                 try:
                    file.save(nombre2)
                 except Exception as inst:
                    #print(inst.args)
                    db.session.delete(nueva_tarea)
                    db.session.commit()
                    return {"msg":"Error subiendo archivo. Tarea NO Creada."}            
                 return tarea_schema.dump(nueva_tarea)
        return {"msg":"Archivo NO Valido."}
     
    def get(self, id_usuario):
        print('VISTAtareas get')
        print(id_usuario)
        return "get"
            
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

def nombre_def(nom, id):
   cad='-'+str(id)+'.'
   temp=nom
   temp=temp.replace('.', cad)
   temp=os.path.join('../archivos/input', temp)
   return temp