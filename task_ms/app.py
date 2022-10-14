from task_ms import create_app
from flask_restful import Api
from .vistas import VistaTareas
from .modelos import db
from flask_jwt_extended import JWTManager

flask_app=create_app('default')
app_context=flask_app.app_context()
app_context.push()

db.init_app(flask_app)
db.create_all()

api=Api(flask_app)
api.add_resource(VistaTareas, '/tasks/<int:id_usuario>')

jwt = JWTManager(flask_app)