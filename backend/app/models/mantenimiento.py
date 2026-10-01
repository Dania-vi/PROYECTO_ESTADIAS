from datetime import datetime

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "mantenimientos"
# Esta tabla almacena los registros de soporte realizados
# sobre los equipos de la empresa.
class Mantenimiento(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "mantenimientos"

    # Identificador único del mantenimiento
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Equipo al que se realizó el mantenimiento
    # Es una llave foránea que apunta a equipos.id
    equipo_id: Mapped[int] = mapped_column(
        ForeignKey("equipos.id"),
        nullable=False
    )

    # Técnico que realizó el mantenimiento
    # Es una llave foránea que apunta a tecnicos.id
    tecnico_id: Mapped[int] = mapped_column(
        ForeignKey("tecnicos.id"),
        nullable=False
    )

    # Fecha y hora en que se realizó el mantenimiento
    # Si no se proporciona, se utiliza la fecha y hora actual
    fecha_mantenimiento: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    # Tipo de mantenimiento realizado
    # Por ejemplo: preventivo o correctivo
    tipo_mantenimiento: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Problema detectado durante la intervención
    problema_detectado: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Solución aplicada al problema
    solucion_aplicada: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Tiempo empleado en el mantenimiento, expresado en minutos
    tiempo_empleado_min: Mapped[int | None] = mapped_column(
        nullable=True
    )

    # Información adicional sobre el mantenimiento
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )