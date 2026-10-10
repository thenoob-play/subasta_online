
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from datetime import datetime

from backend.ppp.shemas.usuario import UsuarioCreate 
from backend.ppp.crud.crudRegirstro import crear_registro_usuario , \
    verificar_correo_telefono_existente , obtener_contrasena_por_correo ,\
    obtener_rol_por_correo, \
    validar_documento_cuentaBancaria , crear_registro_vendedor, \
    obtener_datos_para_modificar, modificar_usuarios



#import validaciones
import backend.ppp.heramientas.validaciones as validar_email 
from backend.ppp.heramientas.CrearToken import crear_token_acceso
from backend.ppp.heramientas.validaciones import encriptar_password , verificar_password

def crear_cuenta_usuario(dato):
    nombe = dato["nombre"]
    correo = dato["correo"]
    password = dato["password"]
    telefono = dato["telefono"]
    rol = dato["rol"]
    activo = dato["activo"]
    fecha_registro = dato["fecha_registro"]
    
    
    if nombe is None or correo is None or password is None or telefono is None or rol is None or activo is None or fecha_registro is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan datos")
    
    if len(nombe) < 3 or len(correo) < 6 or len(password) < 6 or len(telefono) < 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Los datos son incorrectos")
    
    if validar_email.validar_email(correo) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo no es correcto")
    
    
    if fecha_registro.date() != datetime.now().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La fecha de registro debe coincidir con el día, mes y año actual"
        )
    #ENUM('vendedor', 'comprador', 'admin')
    if rol not in ["vendedor", "comprador", "admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rol no es correcto")

    
    if verificar_correo_telefono_existente(correo, telefono):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo o teléfono ya existe")
    
    ## encriptar contraseña
    password_encriptado = encriptar_password(password)
    dato["password"] = password_encriptado
    
    mandar_datos = crear_registro_usuario(dato)
    
    if mandar_datos:
        return {"message": "Usuario creado correctamente"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al crear usuario")
    


def login_usuario(dato):
    correo = dato["correo"]
    password = dato["password"]

    if correo is None or password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan datos")
    
    if validar_email.validar_email(correo) is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo no es correcto")
        
    
    password_DataBase = obtener_contrasena_por_correo(correo)
    
    if not password_DataBase:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo no existe")
    
    if verificar_password(password, password_DataBase[0]) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña es incorrecta")
    
    
    rol = obtener_rol_por_correo(correo)
    if rol not in ["comprador", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene un rol habilitado para este inicio de sesión",
        )

    token_data = {"sub": correo, "rol": rol}
    access_token = crear_token_acceso(token_data)
    
    return {
        "message": "usuario logueado correctamente",
        "access_token": access_token,
        "token_type": "bearer"
    }


def modificar_usuario(dato, correo):
    campos_permitidos = {"nombre", "password", "telefono"}
    if len(dato) != 1 or not set(dato).issubset(campos_permitidos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar exactamente un campo: nombre, telefono o password",
        )

    campo, valor = next(iter(dato.items()))
    if valor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo a modificar no puede estar vacío",
        )

    minimo = 6 if campo == "password" else 10 if campo == "telefono" else 3
    if len(valor.strip()) < minimo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor del campo no cumple con la longitud mínima",
        )

    password_actual = obtener_datos_para_modificar(correo)
    if password_actual is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el usuario autenticado",
        )

    if campo == "password":
        if verificar_password(valor, password_actual):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual",
            )
        dato[campo] = encriptar_password(valor)

    if not modificar_usuarios(dato, correo):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo modificar la información del usuario",
        )

    return f"{campo.capitalize()} actualizado correctamente"

def registrar_vendedor(dato):
    # datos de la tabla usuarios
    nombe = dato["nombre"]
    correo = dato["correo"]
    password = dato["password"]
    telefono = dato["telefono"]
    rol = dato["rol"]
    activo = dato["activo"]
    fecha_registro = dato["fecha_registro"]
    # datos de la tabla vendedores
    documento = dato["documento"]
    nombre_comercial = dato["nombre_comercial"]
    direccion = dato["direccion"]
    cuenta_bancaria = dato["cuenta_bancaria"]
    
    
    if nombe is None or correo is None or password is None or telefono is None or rol is None or activo is None or fecha_registro is None or documento is None or nombre_comercial is None or direccion is None or cuenta_bancaria is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan datos")
    
    if len(nombe) < 3 or len(correo) < 6 or len(password) < 6 or len(telefono) < 10 or len(documento) < 6 or len(nombre_comercial) < 3 or len(direccion) < 3 or len(cuenta_bancaria) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Los datos son incorrectos")
    
    if validar_email.validar_email(correo) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo no es correcto")
    
    
    if fecha_registro.date() != datetime.now().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La fecha de registro debe coincidir con el día, mes y año actual"
        )
    if rol != "vendedor":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rol no es correcto")
    
    if verificar_correo_telefono_existente(correo, telefono):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo o teléfono ya existe")
         
    
    if validar_documento_cuentaBancaria(documento, cuenta_bancaria):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El documento o cuenta bancaria ya existe")
    
    ## encriptar contraseña
    password_encriptado = encriptar_password(password)
    dato["password"] = password_encriptado  
    
    try:
        return crear_registro_vendedor(dato)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al registrar vendedor: {err}")
    
    
    
def login_vendedor(dato):
    correo = dato["correo"]
    password = dato["password"]

    if correo is None or password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan datos")
    
    if validar_email.validar_email(correo) is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo no es correcto")
        
    
    password_DataBase = obtener_contrasena_por_correo(correo)
    
    if not password_DataBase:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo no existe")
    
    if verificar_password(password, password_DataBase[0]) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña es incorrecta")
    
    
    token_data = {"sub": correo, "rol": "vendedor"}
    access_token = crear_token_acceso(token_data)
    
    return {
        "message": "Vendedor logueado correctamente",
        "access_token": access_token,
        "token_type": "bearer"
    }