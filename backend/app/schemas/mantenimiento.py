from pydantic import BaseModel, Field


# Esquema para recibir los datos de un mantenimiento nuevo.
class MantenimientoCreate(BaseModel):
    # Los identificadores de equipo y técnico deben ser positivos.
    # La existencia de esos registros la comprueba la clave foránea de PostgreSQL.
    equipo_id: int = Field(gt=0)
    tecnico_id: int = Field(gt=0)

    # Información del mantenimiento.
    tipo_mantenimiento: str | None = Field(default=None, max_length=20)
    problema_detectado: str | None = None
    solucion_aplicada: str | None = None

    # El tiempo empleado se expresa en minutos y no puede ser negativo.
    tiempo_empleado_min: int | None = Field(default=None, ge=0)

    observaciones: str | None = None
