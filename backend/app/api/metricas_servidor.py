from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.metrica_servidor import MetricaServidor
from app.schemas.metrica_servidor import MetricaServidorCreate


# Define las rutas relacionadas con las métricas de los servidores.
router = APIRouter(
    prefix="/api/metricas-servidor",
    tags=["Métricas de servidores"]
)


# Consulta todas las mediciones registradas.
@router.get("/")
def obtener_metricas(db: Session = Depends(get_db)):
    metricas = db.query(MetricaServidor).all()

    # Convierte las mediciones en objetos que FastAPI devuelve como JSON.
    return [
        {
            "id": metrica.id,
            "servidor_id": metrica.servidor_id,
            "fecha_hora": metrica.fecha_hora,
            "cpu_uso_porcentaje": metrica.cpu_uso_porcentaje,
            "ram_uso_porcentaje": metrica.ram_uso_porcentaje,
            "ram_usada_mb": metrica.ram_usada_mb,
            "disco_uso_porcentaje": metrica.disco_uso_porcentaje,
            "disco_libre_gb": metrica.disco_libre_gb,
            "internet_activo": metrica.internet_activo,
            "latencia_ms": metrica.latencia_ms,
        }
        for metrica in metricas
    ]


# Registra una medición nueva para un servidor.
@router.post("/")
def crear_metrica(
    datos: MetricaServidorCreate,
    db: Session = Depends(get_db)
):
    # Construye el registro con los datos recibidos.
    nueva_metrica = MetricaServidor(
        servidor_id=datos.servidor_id,
        cpu_uso_porcentaje=datos.cpu_uso_porcentaje,
        ram_uso_porcentaje=datos.ram_uso_porcentaje,
        ram_usada_mb=datos.ram_usada_mb,
        disco_uso_porcentaje=datos.disco_uso_porcentaje,
        disco_libre_gb=datos.disco_libre_gb,
        internet_activo=datos.internet_activo,
        latencia_ms=datos.latencia_ms,
    )

    # Agrega la medición a la sesión de SQLAlchemy.
    db.add(nueva_metrica)

    try:
        # Intenta guardar la medición en PostgreSQL.
        db.commit()

        # Recupera el ID y la fecha generados por la base de datos.
        db.refresh(nueva_metrica)

    except IntegrityError:
        # Revierte la transacción si se incumple una restricción,
        # por ejemplo, si el servidor indicado no existe.
        db.rollback()

        # Devuelve un error controlado en lugar de un error interno 500.
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar la métrica. "
                "Verifica que el servidor exista y que los datos sean válidos."
            ),
        )

    # Devuelve la medición guardada correctamente.
    return {
        "id": nueva_metrica.id,
        "servidor_id": nueva_metrica.servidor_id,
        "fecha_hora": nueva_metrica.fecha_hora,
        "cpu_uso_porcentaje": nueva_metrica.cpu_uso_porcentaje,
        "ram_uso_porcentaje": nueva_metrica.ram_uso_porcentaje,
        "ram_usada_mb": nueva_metrica.ram_usada_mb,
        "disco_uso_porcentaje": nueva_metrica.disco_uso_porcentaje,
        "disco_libre_gb": nueva_metrica.disco_libre_gb,
        "internet_activo": nueva_metrica.internet_activo,
        "latencia_ms": nueva_metrica.latencia_ms,
    }
