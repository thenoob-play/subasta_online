import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

## import a al archivo crudSubasta.py
from backend.ppp.crud.crudSubasta import (
    cancelar_subasta as cancelar_subasta_crud,
    crear_subasta_con_articulo,
    eliminar_subasta_y_articulo,
    modificar_subasta as modificar_subasta_crud,
)
from backend.ppp.validaciones import validar_fecha_inicio_no_pasada

logger = logging.getLogger(__name__)


def crear_subasta_nuevo(dato , vendedor_correo):
    precio_inicial = dato["precio_inicial"]
    incremento_minimo = dato["incremento_minimo"]
    fecha_inicio = dato["fecha_inicio"]
    fecha_fin = dato["fecha_fin"]
    estado = dato["estado"]

    if precio_inicial < 0 or incremento_minimo <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio inicial no puede ser negativo y el incremento mínimo debe ser mayor que cero",
        )

    ahora = datetime.now(fecha_inicio.tzinfo) if fecha_inicio.tzinfo else datetime.now()
    try:
        validar_fecha_inicio_no_pasada(fecha_inicio, ahora)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err

    if fecha_inicio >= fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio debe ser menor a la fecha de fin",
        )

    if estado not in ["en_curso", "por_empezar"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado debe ser 'en_curso' o 'por_empezar'",
        )

    titulo = dato["titulo"]
    descripcion = dato["descripcion"]
    condicion = dato["condicion"]
    imagenes = dato["imagen_url"]
    categoria = dato["categoria"]

    if len(titulo.strip()) < 3 or len(titulo) > 45:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El título debe tener entre 3 y 45 caracteres",
        )
    if len(descripcion.strip()) < 3 or len(descripcion) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La descripción debe tener entre 3 y 255 caracteres",
        )
    if condicion not in ["nuevo", "bueno", "medio", "malo"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La condición debe ser 'nuevo', 'bueno', 'medio' o 'malo'",
        )
    if not imagenes or len(imagenes) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar entre 1 y 5 imágenes",
        )
    if any(not url.strip() or len(url) > 255 for url in imagenes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cada URL de imagen debe tener entre 1 y 255 caracteres",
        )
    if not categoria.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar una categoría",
        )

    try:
        resultado = crear_subasta_con_articulo(dato, vendedor_correo)
    except LookupError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except Exception as err:
        logger.exception("No se pudo crear la subasta, el artículo y sus imágenes")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo crear la subasta, el artículo y sus imágenes",
        ) from err

    return {
        "message": "Subasta, artículo e imágenes creados correctamente",
        **resultado,
    }


def eliminar_subasta(subasta_id):
    try:
        eliminar_subasta_y_articulo(subasta_id)
    except LookupError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la subasta porque tiene pujas, pagos u otros registros asociados",
        ) from err
    except SQLAlchemyError as err:
        logger.exception("Error eliminando la subasta %s", subasta_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo eliminar la subasta",
        ) from err

    return {"message": "Subasta y artículo eliminados correctamente"}


def cancelar_subasta(subasta_id, vendedor_correo):
    try:
        cancelar_subasta_crud(subasta_id, vendedor_correo)
    except LookupError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except PermissionError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(err),
        ) from err
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        ) from err
    except SQLAlchemyError as err:
        logger.exception("Error cancelando la subasta %s", subasta_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo cancelar la subasta",
        ) from err

    return {"message": "Subasta cancelada correctamente"}



def modificar_subasta(dato, id_subasta, vendedor_correo):
    try:
        modificar_subasta_crud(dato, id_subasta, vendedor_correo)
    except LookupError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except PermissionError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(err),
        ) from err
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except SQLAlchemyError as err:
        logger.exception("Error modificando la subasta %s", id_subasta)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo modificar la subasta",
        ) from err

    return "Subasta modificada correctamente"
