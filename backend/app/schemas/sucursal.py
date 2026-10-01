from pydantic import BaseModel


# Esquema utilizado para recibir los datos
# necesarios para registrar una nueva sucursal.
class SucursalCreate(BaseModel):

    # Nombre de la sucursal.
    nombre: str

    # Dirección física de la sucursal.
    direccion: str | None = None

    # Teléfono de la sucursal.
    telefono: str | None = None

    # Indica si la sucursal se encuentra activa.
    # Por defecto se considera activa.
    activo: bool = True