from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "equipos"
class Equipo(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "equipos"

    # Identificador único del equipo
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Identificador de la sucursal a la que pertenece el equipo
    # Es una llave foránea que apunta a sucursales.id
    sucursal_id: Mapped[int] = mapped_column(
        ForeignKey("sucursales.id"),
        nullable=False
    )

    # Nombre o identificador del equipo
    nombre: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    # Tipo de equipo, por ejemplo: computadora, caja, impresora, etc.
    tipo_equipo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Marca del equipo
    marca: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Modelo del equipo
    modelo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Número de serie del equipo
    numero_serie: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True
    )

    # Estado actual del equipo
    estado: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )