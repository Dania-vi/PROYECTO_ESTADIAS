from pydantic import BaseModel, Field


# Esquema para registrar un equipo nuevo.
class EquipoCreate(BaseModel):
    # Debe indicar una sucursal existente; el ID debe ser positivo.
    sucursal_id: int = Field(gt=0)

    # El nombre es obligatorio y respeta el tamaño de la columna.
    nombre: str = Field(min_length=1, max_length=80)

    # Los campos opcionales respetan los tamaños definidos en la base de datos.
    tipo_equipo: str | None = Field(default=None, max_length=50)
    marca: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=50)
    numero_serie: str | None = Field(default=None, max_length=80)
    estado: str | None = Field(default=None, max_length=30)
