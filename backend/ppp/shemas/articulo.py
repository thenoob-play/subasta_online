from datetime import date, datetime, time
from decimal import Decimal
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


FiltroTexto = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=45),
]


class PedirArticulo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: FiltroTexto | None = None
    categoria: FiltroTexto | None = None
    precio_inicial: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    precio_final: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None

    @field_validator("fecha_inicio", mode="before")
    @classmethod
    def convertir_fecha_inicio(cls, fecha):
        if isinstance(fecha, str) and len(fecha) == 10:
            return datetime.combine(date.fromisoformat(fecha), time.min)
        return fecha

    @field_validator("fecha_fin", mode="before")
    @classmethod
    def convertir_fecha_fin(cls, fecha):
        if isinstance(fecha, str) and len(fecha) == 10:
            return datetime.combine(date.fromisoformat(fecha), time.max)
        return fecha

    @field_validator("fecha_inicio", "fecha_fin")
    @classmethod
    def validar_fecha_sin_zona(cls, fecha):
        if fecha is not None and fecha.utcoffset() is not None:
            raise ValueError("Las fechas deben enviarse sin zona horaria")
        return fecha

    @model_validator(mode="after")
    def validar_rangos(self):
        if (
            self.precio_inicial is not None
            and self.precio_final is not None
            and self.precio_inicial > self.precio_final
        ):
            raise ValueError("precio_inicial debe ser menor o igual a precio_final")

        if (
            self.fecha_inicio is not None
            and self.fecha_fin is not None
            and self.fecha_inicio > self.fecha_fin
        ):
            raise ValueError("fecha_inicio debe ser anterior o igual a fecha_fin")

        if (
            self.fecha_inicio is not None
            and self.fecha_fin is not None
            and (self.fecha_inicio.tzinfo is None) != (self.fecha_fin.tzinfo is None)
        ):
            raise ValueError("Las fechas deben usar la misma zona horaria")

        return self


class ArticuloEncontrado(BaseModel):
    id_subasta: int
    id_articulo: int
    titulo: str
    descripcion: str | None
    condicion: str
    categoria: str
    precio_inicial: Decimal
    incremento_minimo: Decimal
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str
    imagenes: list[str]


class ResultadoBusquedaArticulos(BaseModel):
    total: int
    limite: int
    resultados: list[ArticuloEncontrado]
