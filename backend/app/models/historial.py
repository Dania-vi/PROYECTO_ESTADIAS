
from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "historial".
# Almacena los eventos y movimientos importantes
# realizados dentro de los diferentes módulos del sistema.
class Historial(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "historial"

    # Identificador único de cada evento
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Fecha y hora en que ocurrió el evento
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    # Módulo del sistema donde ocurrió el evento
    # Ejemplo: mantenimientos, servidores o respaldos.
    modulo: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Acción que se realizó
    # Ejemplo: creación, modificación o eliminación.
    accion: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Descripción detallada del evento registrado
    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Tipo de registro relacionado con el evento
    # Ejemplo: equipo, servidor o mantenimiento.
    entidad: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Identificador del registro relacionado con el evento
    entidad_id: Mapped[int | None] = mapped_column(
        nullable=True
    )

    # Usuario que realizó la acción.
    # Se deja opcional porque todavía no tenemos
    # implementado un sistema de inicio de sesión.
    usuario: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
