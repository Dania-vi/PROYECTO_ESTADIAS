from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# Modelo que representa la tabla "tecnicos"
class Tecnico(Base):

    # Nombre de la tabla en PostgreSQL
    __tablename__ = "tecnicos"

    # Identificador único del técnico
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Nombre completo del técnico
    nombre: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    # Correo electrónico del técnico
    correo: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # Número telefónico del técnico
    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Indica si el técnico se encuentra activo
    # Por defecto, un técnico nuevo estará activo
    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )