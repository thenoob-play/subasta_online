from fastapi import APIRouter, Depends, status
from backend.ppp.heramientas.CrearToken import verificar_rol_vendedor
from backend.ppp.shemas.subasta import (
    CancelarSubasta,
    CreateSubasta,
    CreateSubastaNuevo,
    deleteSubasta,
    modificarSubasta,
)

# 1. (Opcional pero recomendado) Importa el servicio con otro alias para evitar confusiones
from backend.ppp.services.servicesSubasta import crear_subasta as servicio_crear_subasta
from backend.ppp.services.ServicesSubastaNuevo import (
    cancelar_subasta,
    crear_subasta_nuevo,
    eliminar_subasta,
    modificar_subasta
)

router = APIRouter()

# 2. Cambia el nombre de la función del endpoint para que NO se llame igual
@router.post("/CrearSubasta", status_code=status.HTTP_201_CREATED, response_model=dict)
async def crear_subasta_endpoint(
    subasta_datos: CreateSubasta,
    usuario_actual: dict = Depends(verificar_rol_vendedor)
): 
    vendedor_correo = usuario_actual["correo"]
    
    datos_dict = subasta_datos.model_dump()
    
    # 3. Usa el servicio correcto y añade 'await' si tu función de servicio es async def
    # (Si tu servicio es una función normal 'def', quita el 'await')
    enviar_datos = await servicio_crear_subasta(datos_dict, vendedor_correo)

    return {"message": enviar_datos}


@router.post("/CrearSubastaNuevo", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_subasta_endpoint_nuevo(
    subasta_datos: CreateSubastaNuevo,
):
    vendedor_correo = subasta_datos.vendedor_correo
    datos_dict = subasta_datos.model_dump(exclude={"vendedor_correo"})
    
    # 3. Usa el servicio correcto y añade 'await' si tu función de servicio es async def
    # (Si tu servicio es una función normal 'def', quita el 'await')
    enviar_datos = crear_subasta_nuevo(datos_dict, vendedor_correo)

    return enviar_datos


#eliminar subasta
@router.delete("/EliminarSubasta", status_code=status.HTTP_200_OK, response_model=dict)
def eliminar_subasta_endpoint(
    solicitud: deleteSubasta
    
): 
    #vendedor_correo = usuario_actual["correo"]
    
    # 3. Usa el servicio correcto y añade 'await' si tu función de servicio es async def
    # (Si tu servicio es una función normal 'def', quita el 'await')
    enviar_datos = eliminar_subasta(solicitud.id_subasta)

    return enviar_datos


@router.post("/CancelarSubasta", status_code=status.HTTP_200_OK, response_model=dict)
def cancelar_subasta_endpoint(
    solicitud: CancelarSubasta,
):
    return cancelar_subasta(solicitud.id_subasta, solicitud.vendedor_correo.strip())


# modificar subasta solo la subasta 
@router.put("/ModificarSubasta", status_code=status.HTTP_200_OK, response_model=dict)
def modificar_subasta_endpoint(
    subasta_datos: modificarSubasta,
): 
    datos_dict = subasta_datos.model_dump(
        exclude={"id_subasta", "vendedor_correo"},
        exclude_unset=True,
    )
    enviar_datos = modificar_subasta(
        datos_dict,
        subasta_datos.id_subasta,
        subasta_datos.vendedor_correo,
    )
    
    return {"message": enviar_datos}
