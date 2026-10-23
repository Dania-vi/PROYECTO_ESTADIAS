
# Importa las herramientas necesarias para crear las rutas de la API.
from fastapi import APIRouter, Depends, HTTPException

# Permite trabajar con las sesiones de PostgreSQL.
from sqlalchemy.orm import Session

# Permite identificar errores de integridad de la base de datos.
from sqlalchemy.exc import IntegrityError

# Importa la dependencia que proporciona la sesión de la base de datos.
from app.database.dependencies import get_db

# Importa el modelo de las métricas de los servidores.
from app.models.metrica_servidor import MetricaServidor

# Importa el esquema que valida los datos recibidos.
from app.schemas.metrica_servidor import MetricaServidorCreate

# Importa el servicio que revisa y prepara las alertas automáticas.
from app.services.alertas_automaticas import (
    revisar_metricas_y_generar_alertas,
)


# Define las rutas relacionadas con las métricas de los servidores.
router = APIRouter(
    prefix="/api/metricas-servidor",
    tags=["Métricas de servidores"],
)


# Consulta todas las mediciones registradas.
@router.get("/")
def obtener_metricas(db: Session = Depends(get_db)):
    # Recupera las métricas almacenadas en PostgreSQL.
    metricas = db.query(MetricaServidor).all()

    # Convierte cada medición en un objeto que FastAPI devuelve como JSON.
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


# Registra una medición nueva y revisa si debe generar alertas.
@router.post("/")
def crear_metrica(
    datos: MetricaServidorCreate,
    db: Session = Depends(get_db),
):
    try:
        # Busca la medición anterior del mismo servidor.
        # Es importante hacerlo antes de insertar la nueva medición.
        metrica_anterior = (
            db.query(MetricaServidor)
            .filter(
                MetricaServidor.servidor_id == datos.servidor_id
            )
            .order_by(
                MetricaServidor.fecha_hora.desc(),
                MetricaServidor.id.desc(),
            )
            .first()
        )

        # Si existe una medición anterior, prepara sus valores
        # para que el servicio pueda compararlos con los actuales.
        metricas_anteriores = None

        if metrica_anterior is not None:
            metricas_anteriores = {
                "cpu_uso_porcentaje": (
                    metrica_anterior.cpu_uso_porcentaje
                ),
                "ram_uso_porcentaje": (
                    metrica_anterior.ram_uso_porcentaje
                ),
                "disco_uso_porcentaje": (
                    metrica_anterior.disco_uso_porcentaje
                ),
                "internet_activo": (
                    metrica_anterior.internet_activo
                ),
            }

        # Construye el nuevo registro con los datos recibidos.
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

        # Añade la medición a la transacción actual.
        db.add(nueva_metrica)

        # Envía los valores actuales al servicio de alertas.
        # El servicio añade las alertas a la misma transacción.
        metricas_actuales = {
            "cpu_uso_porcentaje": datos.cpu_uso_porcentaje,
            "ram_uso_porcentaje": datos.ram_uso_porcentaje,
            "ram_usada_mb": datos.ram_usada_mb,
            "disco_uso_porcentaje": datos.disco_uso_porcentaje,
            "disco_libre_gb": datos.disco_libre_gb,
            "internet_activo": datos.internet_activo,
            "latencia_ms": datos.latencia_ms,
        }

        # Revisa los umbrales y prepara las alertas necesarias.
        revisar_metricas_y_generar_alertas(
            db=db,
            servidor_id=datos.servidor_id,
            metricas=metricas_actuales,
            metricas_anteriores=metricas_anteriores,
        )

        # Confirma la medición y sus alertas en una sola transacción.
        db.commit()

        # Recupera los valores generados por PostgreSQL.
        db.refresh(nueva_metrica)

    except IntegrityError:
        # Revierte los cambios si se incumple una restricción.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar la métrica. "
                "Verifica que el servidor exista y que los datos sean válidos."
            ),
        )

    except Exception as error:
        # Revierte la transacción si ocurre otro error.
        db.rollback()

        # Registra el detalle en la terminal para facilitar la revisión.
        print(f"Error al registrar la métrica o sus alertas: {error}")

        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al registrar la métrica y sus alertas.",
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
