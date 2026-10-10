from fastapi import APIRouter, Depends, status

# Importamos las clases de los esquemas
from backend.ppp.shemas import usuario
from backend.ppp.shemas.usuario import UsuarioLogin, UsuarioCreate, \
    UsuarioCreateVendedor , UsuarioLoginVendedor , UsuarioModificar
# Importamos las funciones directamente del servicio
from backend.ppp.services.serviceLoginRegistro import crear_cuenta_usuario, login_usuario, \
    registrar_vendedor, login_vendedor, modificar_usuario as actualizar_usuario
from backend.ppp.heramientas.CrearToken import verificar_rol_usuario

router = APIRouter()

@router.post("/CrearCuenta", status_code=status.HTTP_201_CREATED, response_model=dict)
async def crear_cuenta(usuario: UsuarioCreate):   
    datos_dict = usuario.model_dump()

    # CORREGIDO: Se llama directamente a la función
    enviar_datos = crear_cuenta_usuario(datos_dict)

    return {"message": enviar_datos}


@router.post("/Login", status_code=status.HTTP_200_OK, response_model=dict)
async def login(usuario: UsuarioLogin):
    datos_dict = usuario.model_dump()

    # CORREGIDO: Se llama directamente a la función, sin .login_usuario
    enviar_datos = login_usuario(datos_dict)

    return {"message": enviar_datos}


#modificar un usuario
@router.put("/ModificarUsuario", status_code=status.HTTP_200_OK, response_model=dict)
async def modificar_usuario(
    usuario_modificar: UsuarioModificar,
    usuario_actual: dict = Depends(verificar_rol_usuario),
):
    datos_dict = usuario_modificar.model_dump(exclude_unset=True)
    enviar_datos = actualizar_usuario(datos_dict, correo=usuario_actual["correo"])

    return {"message": enviar_datos}

@router.post("/CrearCuentaVendedor", status_code=status.HTTP_201_CREATED, response_model=dict)
async def crear_cuenta_vendedor(usuario: UsuarioCreateVendedor):   
    datos_dict = usuario.model_dump()

    # CORREGIDO: Se llama directamente a la función
    enviar_datos = registrar_vendedor(datos_dict)

    return {"message": enviar_datos}


@router.post("/LoginVendedor", status_code=status.HTTP_200_OK, response_model=dict)
async def loginVendedor(usuario: UsuarioLoginVendedor):
    datos_dict = usuario.model_dump()

    # CORREGIDO: Se llama directamente a la función, sin .login_usuario
    enviar_datos = login_vendedor(datos_dict)    
    
    return {"message": enviar_datos}