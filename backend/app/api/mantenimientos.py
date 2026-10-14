
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.mantenimiento import Mantenimiento
from app.schemas.mantenimiento import MantenimientoCreate


# Define las rutas relacionadas con los mantenimientos.
router = APIRouter(
    prefix="/api/mantenimientos",
    tags=["Mantenimientos"]
)


# Consulta todos los mantenimientos registrados.
@router.get("/")
def obtener_mantenimientos(db: Session = Depends(get_db)):
    mantenimientos = db.query(Mantenimiento).all()

    # Convierte los registros en datos que FastAPI puede devolver como JSON.
    return [
        {
            "id": mantenimiento.id,
            "equipo_id": mantenimiento.equipo_id,
            "tecnico_id": mantenimiento.tecnico_id,
            "fecha_mantenimiento": mantenimiento.fecha_mantenimiento,
            "tipo_mantenimiento": mantenimiento.tipo_mantenimiento,
            "problema_detectado": mantenimiento.problema_detectado,
            "solucion_aplicada": mantenimiento.solucion_aplicada,
            "tiempo_empleado_min": mantenimiento.tiempo_empleado_min,
            "observaciones": mantenimiento.observaciones,
        }
        for mantenimiento in mantenimientos
    ]


# Registra un nuevo mantenimiento en PostgreSQL.
@router.post("/")
def crear_mantenimiento(
    datos: MantenimientoCreate,
    db: Session = Depends(get_db)
):
    # Construye el registro con los datos recibidos.
    nuevo_mantenimiento = Mantenimiento(
        equipo_id=datos.equipo_id,
        tecnico_id=datos.tecnico_id,
        tipo_mantenimiento=datos.tipo_mantenimiento,
        problema_detectado=datos.problema_detectado,
        solucion_aplicada=datos.solucion_aplicada,
        tiempo_empleado_min=datos.tiempo_empleado_min,
        observaciones=datos.observaciones,
    )

    # Agrega el registro a la sesión de SQLAlchemy.
    db.add(nuevo_mantenimiento)

    try:
        # Intenta guardar el mantenimiento en PostgreSQL.
        db.commit()

        # Recupera el ID y la fecha generados por la base de datos.
        db.refresh(nuevo_mantenimiento)

    except IntegrityError:
        # Revierte la transacción si algún dato incumple
        # una restricción de integridad, como una clave foránea.
        db.rollback()

        # Devuelve un error controlado en lugar de un error interno 500.
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el mantenimiento. "
                "Verifica que el equipo y el técnico existan "
                "y que los datos sean válidos."
            ),
        )

    # Devuelve los datos del mantenimiento registrado correctamente.
    return {
        "id": nuevo_mantenimiento.id,
        "equipo_id": nuevo_mantenimiento.equipo_id,
        "tecnico_id": nuevo_mantenimiento.tecnico_id,
        "fecha_mantenimiento": nuevo_mantenimiento.fecha_mantenimiento,
        "tipo_mantenimiento": nuevo_mantenimiento.tipo_mantenimiento,
        "problema_detectado": nuevo_mantenimiento.problema_detectado,
        "solucion_aplicada": nuevo_mantenimiento.solucion_aplicada,
        "tiempo_empleado_min": nuevo_mantenimiento.tiempo_empleado_min,
        "observaciones": nuevo_mantenimiento.observaciones,
    }
