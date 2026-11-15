
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# Tipos de mantenimiento permitidos en el sistema.
TipoMantenimiento = Literal["Preventivo", "Correctivo"]


# Esquema para registrar un mantenimiento nuevo.
class MantenimientoCreate(BaseModel):

    # Los identificadores deben ser positivos.
    equipo_id: int = Field(gt=0)
    tecnico_id: int = Field(gt=0)

    # El tipo de mantenimiento debe ser una de las opciones permitidas.
    tipo_mantenimiento: TipoMantenimiento

    # Información adicional del mantenimiento.
    problema_detectado: str | None = None
    solucion_aplicada: str | None = None
    tiempo_empleado_min: int | None = Field(default=None, ge=0)
    observaciones: str | None = None

    # Limpiamos los espacios de los campos de texto opcionales.
    @field_validator(
        "problema_detectado",
        "solucion_aplicada",
        "observaciones",
        mode="before"
    )
    @classmethod
    def limpiar_textos(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip()
            return valor if valor else None

        return valor


# Esquema para actualizar un mantenimiento existente.
class MantenimientoUpdate(BaseModel):

    # Todos los campos son opcionales para permitir actualizaciones parciales.
    equipo_id: int | None = Field(default=None, gt=0)
    tecnico_id: int | None = Field(default=None, gt=0)
    tipo_mantenimiento: TipoMantenimiento | None = None

    problema_detectado: str | None = None
    solucion_aplicada: str | None = None
    tiempo_empleado_min: int | None = Field(default=None, ge=0)
    observaciones: str | None = None

    # Aplicamos la misma limpieza a los campos de texto.
    @field_validator(
        "problema_detectado",
        "solucion_aplicada",
        "observaciones",
        mode="before"
    )
    @classmethod
    def limpiar_textos(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip()
            return valor if valor else None

        return valor
