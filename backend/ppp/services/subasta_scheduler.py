import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from backend.ppp.crud.crudSubasta import actualizar_estados_subastas

logger = logging.getLogger(__name__)
INTERVALO_ACTUALIZACION_SEGUNDOS = 60


async def _actualizar_estados_periodicamente() -> None:
    while True:
        try:
            resultado = await asyncio.to_thread(actualizar_estados_subastas)
            logger.info("Estados de subastas actualizados: %s", resultado)
        except Exception:
            logger.exception("Falló la actualización automática de estados de subastas")

        await asyncio.sleep(INTERVALO_ACTUALIZACION_SEGUNDOS)


@asynccontextmanager
async def subasta_lifespan(app: FastAPI) -> AsyncIterator[None]:
    tarea_actualizacion = asyncio.create_task(_actualizar_estados_periodicamente())
    try:
        yield
    finally:
        tarea_actualizacion.cancel()
        try:
            await tarea_actualizacion
        except asyncio.CancelledError:
            pass
