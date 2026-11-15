
from pydantic import BaseModel, Field, field_validator


# Campos opcionales que deben limpiarse antes de guardarse.
CAMPOS_TEXTO_OPCIONALES = ("correo", "telefono")


# Esquema para registrar un técnico nuevo.
class TecnicoCreate(BaseModel):

    # El nombre es obligatorio y respeta el tamaño de la columna.
    nombre: str = Field(min_length=1, max_length=120)

    # Datos opcionales con límites acordes con PostgreSQL.
    correo: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)

    # Por defecto, el técnico se considera activo.
    activo: bool = True

    # Elimina espacios al inicio y al final y rechaza nombres vacíos.
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del técnico no puede estar vacío.")

        return valor

    # Limpia los campos opcionales y convierte cadenas vacías en None.
    @field_validator(*CAMPOS_TEXTO_OPCIONALES)
    @classmethod
    def limpiar_campos_opcionales(cls, valor):
        if valor is None:
            return None

        valor = valor.strip()

        return valor if valor else None


# Esquema para actualizar un técnico existente.
class TecnicoUpdate(BaseModel):

    # Todos los campos son opcionales para permitir actualizaciones parciales.
    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=120
    )

    correo: str | None = Field(
        default=None,
        max_length=100
    )

    telefono: str | None = Field(
        default=None,
        max_length=20
    )

    # Permite activar o desactivar al técnico.
    activo: bool | None = None

    # Limpia el nombre únicamente cuando se proporciona.
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del técnico no puede estar vacío.")

        return valor

    # Limpia los campos opcionales y convierte cadenas vacías en None.
    @field_validator(*CAMPOS_TEXTO_OPCIONALES)
    @classmethod
    def limpiar_campos_opcionales(cls, valor):
        if valor is None:
            return None

        valor = valor.strip()

        return valor if valor else None
