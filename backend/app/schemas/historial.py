
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Esquema para recibir los datos de un nuevo evento.
class HistorialCreate(BaseModel):
    modulo: str
    accion: str
    descripcion: str
    entidad: str | None = None
    entidad_id: int | None = None
    usuario: str | None = None


# Esquema para devolver los datos de un evento registrado.
class HistorialResponse(BaseModel):
    id: int
    fecha_hora: datetime
    modulo: str
    accion: str
    descripcion: str
    entidad: str | None
    entidad_id: int | None
    usuario: str | None

    # Permite convertir objetos de SQLAlchemy a respuestas Pydantic.
    model_config = ConfigDict(from_attributes=True)
