
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.tecnico import Tecnico
from app.schemas.tecnico import TecnicoCreate


# Define las rutas relacionadas con los técnicos.
router = APIRouter(
    prefix="/api/tecnicos",
    tags=["Técnicos"]
)


# Consulta todos los técnicos registrados.
@router.get("/")
def obtener_tecnicos(db: Session = Depends(get_db)):
    tecnicos = db.query(Tecnico).all()

    # Convierte los registros en datos que FastAPI devuelve como JSON.
    return [
        {
            "id": tecnico.id,
            "nombre": tecnico.nombre,
            "correo": tecnico.correo,
            "telefono": tecnico.telefono,
            "activo": tecnico.activo,
        }
        for tecnico in tecnicos
    ]


# Registra un técnico nuevo.
@router.post("/")
def crear_tecnico(datos: TecnicoCreate, db: Session = Depends(get_db)):
    # Construye el nuevo técnico con los datos recibidos.
    nuevo_tecnico = Tecnico(
        nombre=datos.nombre,
        correo=datos.correo,
        telefono=datos.telefono,
        activo=datos.activo,
    )

    # Agrega el registro a la sesión de SQLAlchemy.
    db.add(nuevo_tecnico)

    try:
        # Guarda los cambios en PostgreSQL.
        db.commit()

        # Recupera los datos generados por la base de datos.
        db.refresh(nuevo_tecnico)

    except IntegrityError:
        # Revierte la transacción si se incumple una restricción.
        db.rollback()

        # Devuelve un error controlado en lugar de un error interno 500.
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el técnico. "
                "Verifica que los datos sean válidos."
            ),
        )

    # Devuelve el técnico registrado correctamente.
    return {
        "id": nuevo_tecnico.id,
        "nombre": nuevo_tecnico.nombre,
        "correo": nuevo_tecnico.correo,
        "telefono": nuevo_tecnico.telefono,
        "activo": nuevo_tecnico.activo,
    }
