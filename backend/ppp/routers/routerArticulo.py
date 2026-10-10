from fastapi import APIRouter, Depends

from backend.ppp.heramientas.CrearToken import verificar_rol_usuario
from backend.ppp.shemas.articulo import (
    PedirArticulo,
    ResultadoBusquedaArticulos,
)
from backend.ppp.services.servicesArituculo import service_pedir_articulo

router = APIRouter()

@router.post(
    "/pedirArticulo",
    response_model=ResultadoBusquedaArticulos,
    dependencies=[Depends(verificar_rol_usuario)],
)
def pedir_articulos(pedir_articulo: PedirArticulo):
    filtros = pedir_articulo.model_dump(exclude_none=True)
    return service_pedir_articulo(filtros)