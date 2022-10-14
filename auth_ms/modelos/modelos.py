# encoding: utf8
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

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