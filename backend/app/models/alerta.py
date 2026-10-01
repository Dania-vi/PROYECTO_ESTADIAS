from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "alertas".
# Almacena las alertas generadas por el sistema,
# tanto por problemas de monitoreo como por fallos en respaldos.
class Alerta(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "alertas"

    # Identificador único de la alerta
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Servidor relacionado con la alerta.
    # Es opcional porque no todas las alertas tienen
    # que estar relacionadas con un servidor.
    servidor_id: Mapped[int | None] = mapped_column(
        ForeignKey("servidores.id"),
        nullable=True
    )

    # Respaldo relacionado con la alerta.
    # Es opcional porque una alerta puede ser de monitoreo
    # y no necesariamente de un respaldo.
    respaldo_id: Mapped[int | None] = mapped_column(
        ForeignKey("respaldos.id"),
        nullable=True
    )

    # Fecha y hora en que se generó la alerta
    fecha_hora: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    # Tipo de alerta generada
    tipo_alerta: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    # Métrica que provocó la alerta, si corresponde
    # Por ejemplo: CPU, RAM, disco o Internet.
    metrica_afectada: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    # Valor registrado cuando se generó la alerta
    valor_registrado: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Nivel de la alerta
    # Por ejemplo: advertencia o problema.
    nivel_alerta: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Mensaje descriptivo de la alerta
    mensaje: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Indica si la notificación de la alerta fue enviada
    # por correo electrónico.
    correo_enviado: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )