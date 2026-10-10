from datetime import datetime  # <-- Cambia 'import datetime' por esto
from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    telefono: str
    rol: str
    activo: bool
    fecha_registro: datetime  # Ahora sí es el tipo de dato correcto
    
class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str
    
    
class UsuarioCreateVendedor(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    telefono: str
    rol: str
    activo: bool
    fecha_registro: datetime  # Ahora sí es el tipo de dato correcto
    documento: str
    nombre_comercial: str
    direccion: str
    cuenta_bancaria: str
    
class UsuarioLoginVendedor(BaseModel):
    correo: EmailStr
    password: str
    
class UsuarioModificar(BaseModel):
    nombre: str | None = None
    password: str | None = None
    telefono: str | None = None

    model_config = {"extra": "forbid"}
    