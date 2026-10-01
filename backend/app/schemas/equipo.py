from pydantic import BaseModel


# Esquema utilizado para recibir los datos
# necesarios para registrar un nuevo equipo.
class EquipoCreate(BaseModel):

    # Identificador de la sucursal a la que pertenece el equipo.
    # Este valor debe corresponder a una sucursal existente.
    sucursal_id: int

    # Nombre o identificador del equipo.
    nombre: str

    # Tipo de equipo, por ejemplo: computadora, caja, impresora, etc.
    tipo_equipo: str | None = None

    # Marca del equipo.
    marca: str | None = None

    # Modelo del equipo.
    modelo: str | None = None

    # Número de serie del equipo.
    numero_serie: str | None = None

    # Estado actual del equipo.
    estado: str | None = None