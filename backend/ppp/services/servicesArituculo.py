import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from backend.ppp.crud.crudArticulo import (
    MAX_ARTICULOS_POR_BUSQUEDA,
    buscar_articulos,
)

logger = logging.getLogger(__name__)


def service_pedir_articulo(datos):
    filtros = {
        nombre: valor
        for nombre, valor in datos.items()
        if valor is not None
    }

    try:
        resultados = buscar_articulos(filtros)
    except SQLAlchemyError as err:
        logger.exception("Error consultando artículos y subastas")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudieron consultar los artículos",
        ) from err

    return {
        "total": len(resultados),
        "limite": MAX_ARTICULOS_POR_BUSQUEDA,
        "resultados": resultados,
    }
