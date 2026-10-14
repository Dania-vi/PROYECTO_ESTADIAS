from pydantic import BaseModel, Field


# Esquema para recibir los datos de una sucursal nueva.
class SucursalCreate(BaseModel):
    # El nombre es obligatorio y debe respetar el tamaño de la columna.
    nombre: str = Field(min_length=1, max_length=100)

    direccion: str | None = None
    telefono: str | None = Field(default=None, max_length=20)

    # Por defecto, la sucursal se considera activa.
    activo: bool = True
