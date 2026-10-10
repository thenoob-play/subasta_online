import os
from pathlib import Path
import token
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# Construye la ruta absoluta o relativa hacia el archivo .env según su ubicación
# Por ejemplo, si está en la misma carpeta o subiendo niveles:
env_path = Path(__file__).resolve().parent.parent.parent / '.env' # Ajusta los .parent según corresponda
load_dotenv(dotenv_path=env_path)

# O si sabes exactamente dónde está respecto a este archivo:
# load_dotenv(dotenv_path="../.env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No se encontró la variable de entorno SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256") # Valor por defecto HS256 si no está en el .env

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/LoginVendedor")

def crear_token_acceso(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_rol_vendedor(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub") or payload.get("correo")
        rol: str = payload.get("rol")
        
        if correo is None or rol is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    if rol != "vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere una cuenta de vendedor."
        )
    return {"correo": correo, "rol": rol}


def verificar_rol_usuario(token: str = Depends(oauth2_scheme)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub") or payload.get("correo")
        rol: str = payload.get("rol")
        
        if correo is None or rol is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    if rol not in ("comprador", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere una cuenta de comprador o administrador."
        )
    return {"correo": correo, "rol": rol}    