
from pydantic import BaseModel, Field


# Esquema para recibir los datos de un servidor nuevo.
class ServidorCreate(BaseModel):

    # El nombre del host es obligatorio.
    nombre_host: str = Field(min_length=1, max_length=80)

    # La dirección IP se recibe como texto.
    direccion_ip: str | None = Field(default=None, max_length=45)

    # Sistema operativo instalado en el servidor.
    sistema_operativo: str | None = Field(default=None, max_length=80)

    # Estado actual del servidor.
    estado_actual: str | None = Field(default=None, max_length=20)


# Esquema para actualizar la información de un servidor existente.
class ServidorUpdate(BaseModel):

    # Nombre del host que identifica al servidor.
    nombre_host: str = Field(min_length=1, max_length=80)

    # Dirección IP del servidor.
    direccion_ip: str | None = Field(default=None, max_length=45)

    # Sistema operativo instalado.
    sistema_operativo: str | None = Field(default=None, max_length=80)

    # Estado actual del servidor.
    estado_actual: str | None = Field(default=None, max_length=20)
