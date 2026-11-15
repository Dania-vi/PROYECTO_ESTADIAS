
from pydantic import BaseModel, Field, field_validator


# Esquema para recibir los datos de una sucursal nueva.
class SucursalCreate(BaseModel):

    # El nombre es obligatorio y debe respetar el tamaño de la columna.
    nombre: str = Field(min_length=1, max_length=100)

    # Datos opcionales de la sucursal.
    direccion: str | None = None
    telefono: str | None = Field(default=None, max_length=20)

    # Por defecto, la sucursal se considera activa.
    activo: bool = True

    # Elimina espacios al inicio y al final y rechaza nombres vacíos.
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre de la sucursal no puede estar vacío.")

        return valor


# Esquema para actualizar los datos de una sucursal existente.
class SucursalUpdate(BaseModel):

    # Todos los campos son opcionales para permitir actualizaciones parciales.
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    direccion: str | None = None
    telefono: str | None = Field(default=None, max_length=20)
    activo: bool | None = None

    # Valida el nombre únicamente cuando se proporciona como texto.
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        if valor is None:
            return valor

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre de la sucursal no puede estar vacío.")

        return valor
