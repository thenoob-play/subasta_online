from datetime import datetime  # <-- Cambia 'import datetime' por esto
import re
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from typing import List

class CreateSubastaBase(BaseModel):
    precio_inicial: float
    incremento_minimo: float
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str
    titulo: str
    descripcion: str
    condicion: str
    imagen_url: List[str]
    categoria: str

    @field_validator("fecha_inicio", "fecha_fin", mode="before")
    @classmethod
    def aceptar_fecha_hasta_hora(cls, valor):
        if isinstance(valor, str) and re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}",
            valor,
        ):
            return datetime.strptime(valor, "%Y-%m-%dT%H")
        return valor


class CreateSubasta(CreateSubastaBase):
    precio_actual: float


class CreateSubastaNuevo(CreateSubastaBase):
    vendedor_correo: str
    
class deleteSubasta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_subasta: int = Field(
        gt=0,
        strict=True,
        validation_alias=AliasChoices("id_subasta", "subasta_id"),
    )


class CancelarSubasta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vendedor_correo: str = Field(min_length=3, max_length=100)
    id_subasta: int = Field(gt=0, strict=True)

    @field_validator("vendedor_correo")
    @classmethod
    def validar_correo_vendedor(cls, valor: str) -> str:
        correo = valor.strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            raise ValueError("Debe proporcionar un correo válido de vendedor")
        return correo



class modificarSubasta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    id_subasta: int = Field(gt=0, strict=True)
    vendedor_correo: str = Field(min_length=3, max_length=100)
    precio_inicial: float | None = Field(default=None, ge=0)
    incremento_minimo: float | None = Field(default=None, gt=0)
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    estado: str | None = Field(default=None, pattern="^(en_curso|por_empezar)$")

    @field_validator("vendedor_correo")
    @classmethod
    def validar_correo_vendedor(cls, valor: str) -> str:
        correo = valor.strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            raise ValueError("Debe proporcionar un correo válido de vendedor")
        return correo

    @field_validator("fecha_inicio", "fecha_fin", mode="before")
    @classmethod
    def aceptar_fecha_hasta_hora(cls, valor):
        if isinstance(valor, str) and re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}",
            valor,
        ):
            return datetime.strptime(valor, "%Y-%m-%dT%H")
        return valor