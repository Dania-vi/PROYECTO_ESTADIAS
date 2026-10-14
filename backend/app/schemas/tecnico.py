from pydantic import BaseModel, Field


# Esquema para recibir los datos de un técnico nuevo.
class TecnicoCreate(BaseModel):
    # El nombre es obligatorio y respeta el tamaño de la columna.
    nombre: str = Field(min_length=1, max_length=120)

    # Datos opcionales con límites acordes con la base de datos.
    correo: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)

    # Por defecto, el técnico se considera activo.
    activo: bool = True
