from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "servidores"
# Almacena la información básica de los servidores
# que serán monitoreados por el sistema.
class Servidor(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "servidores"

    # Identificador único del servidor
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Nombre del host o nombre identificador del servidor
    nombre_host: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    # Dirección IP del servidor
    direccion_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )

    # Sistema operativo instalado en el servidor
    sistema_operativo: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True
    )

    # Estado actual del servidor
    estado_actual: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Fecha y hora de la última conexión registrada
    ultima_conexion: Mapped[datetime | None] = mapped_column(
        nullable=True
    )