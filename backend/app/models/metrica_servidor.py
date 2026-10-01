from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "metricas_servidor"
# Almacena las mediciones obtenidas periódicamente
# de los servidores que son monitoreados.
class MetricaServidor(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "metricas_servidor"

    # Identificador único de la medición.
    # BigInteger corresponde al tipo "bigint" de PostgreSQL.
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    # Identificador del servidor al que pertenece la medición.
    # Es una llave foránea que apunta a servidores.id.
    servidor_id: Mapped[int] = mapped_column(
        ForeignKey("servidores.id"),
        nullable=False
    )

    # Fecha y hora en que se registró la medición.
    fecha_hora: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    # Porcentaje de uso del CPU.
    # Numeric(5, 2) permite valores como 75.50.
    cpu_uso_porcentaje: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    # Porcentaje de memoria RAM utilizada.
    ram_uso_porcentaje: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    # Cantidad de RAM utilizada en MB.
    ram_usada_mb: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    # Porcentaje de espacio utilizado en disco.
    disco_uso_porcentaje: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    # Espacio disponible en disco expresado en GB.
    disco_libre_gb: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    # Indica si el servidor tiene conexión a Internet.
    internet_activo: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    # Latencia de conexión expresada en milisegundos.
    latencia_ms: Mapped[int | None] = mapped_column(
        nullable=True
    )