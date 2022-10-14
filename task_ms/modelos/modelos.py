import enum
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.sql import func

db = SQLAlchemy()

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