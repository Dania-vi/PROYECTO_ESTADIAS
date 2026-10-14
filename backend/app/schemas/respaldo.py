from pydantic import BaseModel, Field


# Esquema para recibir los datos de un respaldo nuevo.
class RespaldoCreate(BaseModel):
    # El equipo es obligatorio y su ID debe ser positivo.
    equipo_id: int = Field(gt=0)

    # El servidor es opcional; si se proporciona, su ID debe ser positivo.
    servidor_id: int | None = Field(default=None, gt=0)

    tipo_respaldo: str | None = Field(default=None, max_length=30)

    # El tamaño del respaldo se expresa en MB y no puede ser negativo.
    tamanio_mb: float | None = Field(
        default=None, ge=0, allow_inf_nan=False
    )

    resultado: str | None = Field(default=None, max_length=20)
    dispositivo_externo: str | None = Field(default=None, max_length=100)
    ruta_destino: str | None = Field(default=None, max_length=255)
    detalles_error: str | None = None
