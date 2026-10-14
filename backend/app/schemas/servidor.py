from pydantic import BaseModel, Field


# Esquema para recibir los datos de un servidor nuevo.
class ServidorCreate(BaseModel):
    # El nombre del host es obligatorio.
    nombre_host: str = Field(min_length=1, max_length=80)

    # La dirección IP se recibe como texto; se limita al tamaño de la columna.
    direccion_ip: str | None = Field(default=None, max_length=45)

    sistema_operativo: str | None = Field(default=None, max_length=80)
    estado_actual: str | None = Field(default=None, max_length=20)
