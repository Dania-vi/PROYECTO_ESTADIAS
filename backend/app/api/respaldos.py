from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.respaldo import Respaldo
from app.schemas.respaldo import RespaldoCreate


# Define las rutas de la API relacionadas con los respaldos.
router = APIRouter(
    prefix="/api/respaldos",
    tags=["Respaldos"]
)


# Consulta todos los respaldos registrados.
@router.get("/")
def obtener_respaldos(db: Session = Depends(get_db)):
    respaldos = db.query(Respaldo).all()

    # Convierte los registros en objetos que FastAPI devuelve como JSON.
    return [
        {
            "id": respaldo.id,
            "equipo_id": respaldo.equipo_id,
            "servidor_id": respaldo.servidor_id,
            "fecha_hora": respaldo.fecha_hora,
            "tipo_respaldo": respaldo.tipo_respaldo,
            "tamanio_mb": respaldo.tamanio_mb,
            "resultado": respaldo.resultado,
            "dispositivo_externo": respaldo.dispositivo_externo,
            "ruta_destino": respaldo.ruta_destino,
            "detalles_error": respaldo.detalles_error,
        }
        for respaldo in respaldos
    ]


# Registra un respaldo nuevo en PostgreSQL.
@router.post("/")
def crear_respaldo(
    datos: RespaldoCreate,
    db: Session = Depends(get_db)
):
    # Construye el respaldo con los datos recibidos.
    nuevo_respaldo = Respaldo(
        equipo_id=datos.equipo_id,
        servidor_id=datos.servidor_id,
        tipo_respaldo=datos.tipo_respaldo,
        tamanio_mb=datos.tamanio_mb,
        resultado=datos.resultado,
        dispositivo_externo=datos.dispositivo_externo,
        ruta_destino=datos.ruta_destino,
        detalles_error=datos.detalles_error,
    )

    # Agrega el respaldo a la sesión de SQLAlchemy.
    db.add(nuevo_respaldo)

    try:
        # Intenta guardar el respaldo en PostgreSQL.
        db.commit()

        # Recupera el ID y la fecha generados por la base de datos.
        db.refresh(nuevo_respaldo)

    except IntegrityError:
        # Revierte la transacción si se incumple una restricción,
        # por ejemplo, si el equipo o servidor no existen.
        db.rollback()

        # Devuelve un error controlado en lugar de un error interno 500.
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el respaldo. "
                "Verifica que el equipo exista y que, si proporcionaste "
                "un servidor, también exista. Comprueba que los datos sean válidos."
            ),
        )

    # Devuelve los datos del respaldo registrado correctamente.
    return {
        "id": nuevo_respaldo.id,
        "equipo_id": nuevo_respaldo.equipo_id,
        "servidor_id": nuevo_respaldo.servidor_id,
        "fecha_hora": nuevo_respaldo.fecha_hora,
        "tipo_respaldo": nuevo_respaldo.tipo_respaldo,
        "tamanio_mb": nuevo_respaldo.tamanio_mb,
        "resultado": nuevo_respaldo.resultado,
        "dispositivo_externo": nuevo_respaldo.dispositivo_externo,
        "ruta_destino": nuevo_respaldo.ruta_destino,
        "detalles_error": nuevo_respaldo.detalles_error,
    }
