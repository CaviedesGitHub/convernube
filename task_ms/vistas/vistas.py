from flask_restful import Resource
from flask import request, session, send_file
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
                 nueva_tarea = Tarea(id_usr=user_jwt, nom_arch=filename, ext_conv=ExtSound[request.form.get('tipo')])                   
                 db.session.add(nueva_tarea)
                 db.session.commit()
                 nombre2=nombre_input(filename, nueva_tarea.id)      
                 print(nombre2)              
                 try:
                    file.save(nombre2)
                 except Exception as inst:
                    #print(inst.args)
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
        user_jwt=int(get_jwt_identity())
        tarea=Tarea.query.get_or_404(id_task)
        if tarea.id_usr!=user_jwt:
           return  {"Msg":"Usuario desautorizado."}
        return tarea_schema.dump(tarea)

    @jwt_required()
    def put(self, id_task):
        user_jwt=int(get_jwt_identity())
        tarea=Tarea.query.with_for_update().get_or_404(id_task)
        if tarea.id_usr!=user_jwt:
           db.session.rollback()
           return  {"Msg":"Usuario desautorizado."}
        if tarea.estado==EstadoTarea.PROCESSED:
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
        nombre=nombre_input(tarea.nom_arch, tarea.id)
        if os.path.exists(nombre):
           os.remove(nombre)
        print("borrar el archivo Original")
        if tarea.estado==EstadoTarea.PROCESSED:
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
        if request.get_json()['archivo']=="INPUT":
           nombre=nombre_input(tarea.nom_arch, tarea.id)
        else:
           nombre=nombre_output(tarea.nom_arch, tarea.id, tarea.ext_conv.name.lower())
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
   #temp=os.path.join('../archivos/input', temp)
   #temp='/home/luis/Desarrollo/repo/nube/convernube/archivos/'+'input/'+temp
   temp='../archivos/'+'input/'+temp
   return temp

def nombre_output(nom, id, ext):
   temp=nom
   temp=temp.replace('.', '-'+str(id)+'.')
   temp=os.path.splitext(temp)[0]+'.'+ext.lower()
   temp='../archivos/'+'output/'+temp
   return temp