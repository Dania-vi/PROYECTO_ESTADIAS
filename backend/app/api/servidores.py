from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.servidor import Servidor
from app.schemas.servidor import ServidorCreate


# Define las rutas de la API relacionadas con los servidores.
router = APIRouter(
    prefix="/api/servidores",
    tags=["Servidores"]
)


# Consulta todos los servidores registrados en PostgreSQL.
@router.get("/")
def obtener_servidores(db: Session = Depends(get_db)):
    servidores = db.query(Servidor).all()

    # Convierte los registros en una lista de objetos JSON.
    return [
        {
            "id": servidor.id,
            "nombre_host": servidor.nombre_host,
            "direccion_ip": servidor.direccion_ip,
            "sistema_operativo": servidor.sistema_operativo,
            "estado_actual": servidor.estado_actual,
            "ultima_conexion": servidor.ultima_conexion,
        }
        for servidor in servidores
    ]


# Registra un servidor nuevo en la base de datos.
@router.post("/")
def crear_servidor(
    datos: ServidorCreate,
    db: Session = Depends(get_db)
):
    # Construye el servidor con los datos recibidos.
    nuevo_servidor = Servidor(
        nombre_host=datos.nombre_host,
        direccion_ip=datos.direccion_ip,
        sistema_operativo=datos.sistema_operativo,
        estado_actual=datos.estado_actual,
        ultima_conexion=None,
    )

    # Agrega el servidor a la sesión de SQLAlchemy.
    db.add(nuevo_servidor)

    try:
        # Guarda el nuevo registro en PostgreSQL.
        db.commit()

        # Recupera el identificador generado por la base de datos.
        db.refresh(nuevo_servidor)

    except IntegrityError:
        # Revierte la transacción si se incumple una restricción.
        db.rollback()

        # Devuelve un error controlado en lugar de un error interno 500.
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el servidor. "
                "Verifica que los datos sean válidos."
            ),
        )

    # Devuelve los datos del servidor registrado correctamente.
    return {
        "id": nuevo_servidor.id,
        "nombre_host": nuevo_servidor.nombre_host,
        "direccion_ip": nuevo_servidor.direccion_ip,
        "sistema_operativo": nuevo_servidor.sistema_operativo,
        "estado_actual": nuevo_servidor.estado_actual,
        "ultima_conexion": nuevo_servidor.ultima_conexion,
    }
