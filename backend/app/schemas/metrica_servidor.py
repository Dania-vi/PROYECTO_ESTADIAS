from pydantic import BaseModel, Field


# Esquema para recibir una medición de un servidor.
class MetricaServidorCreate(BaseModel):
    # El ID debe ser positivo; PostgreSQL comprobará que el servidor exista.
    servidor_id: int = Field(gt=0)

    # Los porcentajes de uso deben estar entre 0 y 100.
    cpu_uso_porcentaje: float | None = Field(
        default=None, ge=0, le=100, allow_inf_nan=False
    )
    ram_uso_porcentaje: float | None = Field(
        default=None, ge=0, le=100, allow_inf_nan=False
    )
    disco_uso_porcentaje: float | None = Field(
        default=None, ge=0, le=100, allow_inf_nan=False
    )

    # Las cantidades de memoria y disco no pueden ser negativas ni infinitas.
    ram_usada_mb: float | None = Field(
        default=None, ge=0, allow_inf_nan=False
    )
    disco_libre_gb: float | None = Field(
        default=None, ge=0, allow_inf_nan=False
    )

    # Indica si existe conexión a internet.
    internet_activo: bool | None = None

    # La latencia se mide en milisegundos y no puede ser negativa.
    latencia_ms: int | None = Field(default=None, ge=0)
