from auth_ms import create_app
from flask_restful import Api
from .vistas import VistaUsuario, VistaLogIn, VistaSignIn
from flask_jwt_extended import JWTManager
from .modelos import db
from flask_login import current_user, LoginManager

app=create_app('default')
app_context=app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')
api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')

jwt = JWTManager(app)