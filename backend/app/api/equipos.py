
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.equipo import Equipo
from app.schemas.equipo import EquipoCreate


# Define las rutas de la API relacionadas con los equipos.
router = APIRouter(prefix="/api/equipos", tags=["Equipos"])


# Obtiene todos los equipos registrados en la base de datos.
@router.get("/")
def obtener_equipos(db: Session = Depends(get_db)):
    equipos = db.query(Equipo).all()

    # Convierte los registros en una lista de objetos JSON.
    return [
        {
            "id": equipo.id,
            "sucursal_id": equipo.sucursal_id,
            "nombre": equipo.nombre,
            "tipo_equipo": equipo.tipo_equipo,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "numero_serie": equipo.numero_serie,
            "estado": equipo.estado,
        }
        for equipo in equipos
    ]


# Registra un equipo nuevo en la base de datos.
@router.post("/")
def crear_equipo(datos: EquipoCreate, db: Session = Depends(get_db)):
    # Crea el objeto con los datos recibidos desde la API.
    nuevo_equipo = Equipo(
        sucursal_id=datos.sucursal_id,
        nombre=datos.nombre,
        tipo_equipo=datos.tipo_equipo,
        marca=datos.marca,
        modelo=datos.modelo,
        numero_serie=datos.numero_serie,
        estado=datos.estado,
    )

    # Agrega el equipo a la sesión de SQLAlchemy.
    db.add(nuevo_equipo)

    try:
        # Intenta guardar el equipo en PostgreSQL.
        db.commit()

        # Recupera el ID generado por PostgreSQL.
        db.refresh(nuevo_equipo)

    except IntegrityError:
        # Revierte la transacción si PostgreSQL rechaza el registro.
        # Esto permite que la sesión pueda utilizarse nuevamente.
        db.rollback()

        # Devuelve un mensaje claro cuando los datos incumplen
        # una restricción de integridad de la base de datos.
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el equipo. "
                "Verifica que la sucursal exista y que los datos sean válidos."
            ),
        )

    # Devuelve los datos del equipo registrado correctamente.
    return {
        "id": nuevo_equipo.id,
        "sucursal_id": nuevo_equipo.sucursal_id,
        "nombre": nuevo_equipo.nombre,
        "tipo_equipo": nuevo_equipo.tipo_equipo,
        "marca": nuevo_equipo.marca,
        "modelo": nuevo_equipo.modelo,
        "numero_serie": nuevo_equipo.numero_serie,
        "estado": nuevo_equipo.estado,
    }
