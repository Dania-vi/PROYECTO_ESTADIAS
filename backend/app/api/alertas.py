from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.alerta import Alerta
from app.schemas.alerta import AlertaCreate


# Define las rutas de la API relacionadas con las alertas.
router = APIRouter(
    prefix="/api/alertas",
    tags=["Alertas"]
)


# Consulta todas las alertas registradas en PostgreSQL.
@router.get("/")
def obtener_alertas(db: Session = Depends(get_db)):
    alertas = db.query(Alerta).all()

    # Convierte los registros en objetos que FastAPI devuelve como JSON.
    return [
        {
            "id": alerta.id,
            "servidor_id": alerta.servidor_id,
            "respaldo_id": alerta.respaldo_id,
            "fecha_hora": alerta.fecha_hora,
            "tipo_alerta": alerta.tipo_alerta,
            "metrica_afectada": alerta.metrica_afectada,
            "valor_registrado": alerta.valor_registrado,
            "nivel_alerta": alerta.nivel_alerta,
            "mensaje": alerta.mensaje,
            "correo_enviado": alerta.correo_enviado,
        }
        for alerta in alertas
    ]


# Registra una alerta nueva en PostgreSQL.
@router.post("/")
def crear_alerta(
    datos: AlertaCreate,
    db: Session = Depends(get_db)
):
    # Construye la alerta con los datos recibidos.
    nueva_alerta = Alerta(
        servidor_id=datos.servidor_id,
        respaldo_id=datos.respaldo_id,
        tipo_alerta=datos.tipo_alerta,
        metrica_afectada=datos.metrica_afectada,
        valor_registrado=datos.valor_registrado,
        nivel_alerta=datos.nivel_alerta,
        mensaje=datos.mensaje,
        correo_enviado=datos.correo_enviado,
    )

    # Agrega la alerta a la sesión de SQLAlchemy.
    db.add(nueva_alerta)

    try:
        # Intenta guardar la alerta en PostgreSQL.
        db.commit()

        # Recupera el ID y la fecha generados por la base de datos.
        db.refresh(nueva_alerta)

    except IntegrityError:
        # Revierte la transacción si se incumple una restricción,
        # por ejemplo, si el servidor o respaldo no existen.
        db.rollback()

        # Devuelve un error controlado en lugar de un error interno 500.
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar la alerta. "
                "Verifica que el servidor y el respaldo indicados existan "
                "y que los datos sean válidos."
            ),
        )

    # Devuelve los datos de la alerta registrada correctamente.
    return {
        "id": nueva_alerta.id,
        "servidor_id": nueva_alerta.servidor_id,
        "respaldo_id": nueva_alerta.respaldo_id,
        "fecha_hora": nueva_alerta.fecha_hora,
        "tipo_alerta": nueva_alerta.tipo_alerta,
        "metrica_afectada": nueva_alerta.metrica_afectada,
        "valor_registrado": nueva_alerta.valor_registrado,
        "nivel_alerta": nueva_alerta.nivel_alerta,
        "mensaje": nueva_alerta.mensaje,
        "correo_enviado": nueva_alerta.correo_enviado,
    }
