

import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP

class ModelDataUsuario:
    __tablename__ = "usuario"
    
    id = Column(Integer, primary_key=True , autoincrement=True)
    nombre = str(nullable=False)
    correo = str(nullable=False, unique=True)
    password = str(nullable=False)
    telefono = str(nullable=False, unique=True)
    rol = str(nullable=False)
    activo = bool(nullable=False)
    fecha_registro = datetime(nullable=False)
    
