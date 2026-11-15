
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# Estados permitidos para los equipos.
EstadoEquipo = Literal[
    "Activo",
    "Inactivo",
    "En mantenimiento"
]


# Campos opcionales que deben limpiarse antes de guardarse.
CAMPOS_TEXTO_OPCIONALES = (
    "tipo_equipo",
    "marca",
    "modelo",
    "numero_serie"
)


# Esquema para registrar un equipo nuevo.
class EquipoCreate(BaseModel):

    # El ID de la sucursal es obligatorio y debe ser positivo.
    sucursal_id: int = Field(gt=0)

    # El nombre es obligatorio y respeta el tamaño de la columna.
    nombre: str = Field(min_length=1, max_length=80)

    # Los siguientes campos son opcionales.
    tipo_equipo: str | None = Field(default=None, max_length=50)
    marca: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=50)
    numero_serie: str | None = Field(default=None, max_length=80)

    # Si se proporciona un estado, debe pertenecer a los permitidos.
    estado: EstadoEquipo | None = None

    # Limpia el nombre y rechaza valores vacíos o con espacios.
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del equipo no puede estar vacío.")

        return valor

    # Limpia los campos opcionales y convierte cadenas vacías en None.
    @field_validator(*CAMPOS_TEXTO_OPCIONALES)
    @classmethod
    def limpiar_campos_opcionales(cls, valor):
        if valor is None:
            return None

        valor = valor.strip()

        return valor if valor else None


# Esquema para actualizar un equipo existente.
class EquipoUpdate(BaseModel):

    # Todos los campos son opcionales para permitir actualizaciones parciales.
    sucursal_id: int | None = Field(default=None, gt=0)

    # Si se proporciona un nombre, debe respetar la longitud establecida.
    nombre: str | None = Field(default=None, min_length=1, max_length=80)

    # Campos opcionales del equipo.
    tipo_equipo: str | None = Field(default=None, max_length=50)
    marca: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=50)
    numero_serie: str | None = Field(default=None, max_length=80)

    # Solo permite los estados definidos para los equipos.
    estado: EstadoEquipo | None = None

    # Limpia el nombre únicamente cuando se proporciona.
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del equipo no puede estar vacío.")

        return valor

    # Limpia los campos opcionales y convierte cadenas vacías en None.
    @field_validator(*CAMPOS_TEXTO_OPCIONALES)
    @classmethod
    def limpiar_campos_opcionales(cls, valor):
        if valor is None:
            return None

        valor = valor.strip()

        return valor if valor else None
