from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

# Modelo que representa la tabla "sucursales"
class Sucursal(Base):

    # Nombre de la tabla que se creará en PostgreSQL
    __tablename__ = "sucursales"

    # Identificador único de la sucursal
    # primary_key=True indica que es la llave primaria
    # autoincrement=True permite que PostgreSQL genere el número automáticamente
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Nombre de la sucursal
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Dirección física de la sucursal
    direccion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Teléfono de contacto de la sucursal
    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Indica si la sucursal está activa
    # Por defecto, una nueva sucursal estará activa
    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )