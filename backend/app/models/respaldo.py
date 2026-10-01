from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "respaldos".
# Almacena información sobre los respaldos realizados
# en los equipos de la empresa.
class Respaldo(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "respaldos"

    # Identificador único del respaldo
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Equipo desde el cual se realizó el respaldo.
    # Es una llave foránea que apunta a equipos.id.
    equipo_id: Mapped[int] = mapped_column(
        ForeignKey("equipos.id"),
        nullable=False
    )

    # Servidor relacionado con el respaldo.
    # Este campo es opcional porque nuestra estructura
    # permite que servidor_id sea NULL.
    servidor_id: Mapped[int | None] = mapped_column(
        ForeignKey("servidores.id"),
        nullable=True
    )

    # Fecha y hora en que se realizó el respaldo
    fecha_hora: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    # Tipo de respaldo realizado
    tipo_respaldo: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    # Tamaño del respaldo expresado en MB
    tamanio_mb: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    # Resultado de la operación de respaldo
    # Por ejemplo: exitoso o fallido.
    resultado: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Nombre o identificación del dispositivo externo
    # donde se almacena el respaldo.
    dispositivo_externo: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # Ruta donde se guarda el archivo del respaldo
    ruta_destino: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Información adicional cuando ocurre un error
    detalles_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )