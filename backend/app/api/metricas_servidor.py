
# Importa las herramientas necesarias para crear las rutas de la API.
from fastapi import APIRouter, Depends, HTTPException

# Permite trabajar con las sesiones de PostgreSQL.
from sqlalchemy.orm import Session

# Permite identificar errores de integridad de la base de datos.
from sqlalchemy.exc import IntegrityError

# Permite registrar errores durante el envío de correos.
import logging

# Importa la dependencia que proporciona la sesión de la base de datos.
from app.database.dependencies import get_db

# Importa los modelos de métricas y servidores.
from app.models.metrica_servidor import MetricaServidor
from app.models.servidor import Servidor

# Importa el esquema que valida los datos recibidos.
from app.schemas.metrica_servidor import MetricaServidorCreate

# Importa el servicio que revisa y prepara las alertas automáticas.
from app.services.alertas_automaticas import (
    revisar_metricas_y_generar_alertas,
)

# Importa el servicio encargado de enviar correos electrónicos.
from app.services.correo import enviar_correo_alerta


# Configura el registro de errores de este módulo.
logger = logging.getLogger(__name__)


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
    # Aquí guardaremos las alertas creadas por esta medición.
    alertas_nuevas = []

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
        # para compararlos con los actuales.
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

        # Prepara los valores actuales para revisar los umbrales.
        metricas_actuales = {
            "cpu_uso_porcentaje": datos.cpu_uso_porcentaje,
            "ram_uso_porcentaje": datos.ram_uso_porcentaje,
            "ram_usada_mb": datos.ram_usada_mb,
            "disco_uso_porcentaje": datos.disco_uso_porcentaje,
            "disco_libre_gb": datos.disco_libre_gb,
            "internet_activo": datos.internet_activo,
            "latencia_ms": datos.latencia_ms,
        }

        # Revisa los umbrales y obtiene las alertas que se generaron.
        alertas_nuevas = revisar_metricas_y_generar_alertas(
            db=db,
            servidor_id=datos.servidor_id,
            metricas=metricas_actuales,
            metricas_anteriores=metricas_anteriores,
        )

        # Guarda la medición y todas sus alertas en una sola transacción.
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

        # Registra el detalle para facilitar la revisión.
        logger.exception(
            "Error al registrar la métrica o sus alertas: %s",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al registrar la métrica y sus alertas.",
        )

    # ---------------------------------------------------------
    # ENVÍO AGRUPADO DE CORREOS
    # ---------------------------------------------------------

    # Solo intenta enviar un correo si se generaron alertas nuevas.
    if alertas_nuevas:

        try:
            # Busca el nombre del servidor relacionado con las alertas.
            servidor = db.query(Servidor).filter(
                Servidor.id == datos.servidor_id
            ).first()

            # Si no se encuentra el nombre, utiliza el identificador.
            nombre_servidor = (
                servidor.nombre_host
                if servidor
                else f"Servidor ID {datos.servidor_id}"
            )

            # Construye el contenido del correo con todas las alertas.
            detalles_alertas = []

            for alerta in alertas_nuevas:
                detalles_alertas.append(
                    f"""
Métrica: {alerta.metrica_afectada or 'No especificada'}
Valor: {alerta.valor_registrado or 'No especificado'}
Nivel: {alerta.nivel_alerta or 'Sin clasificar'}
Descripción: {alerta.mensaje or 'Sin descripción'}
"""
                )

            # Agrupa todas las alertas en un solo mensaje.
            asunto = (
                f"Alertas de monitoreo - {nombre_servidor} "
                f"({len(alertas_nuevas)} alertas)"
            )

            mensaje = f"""
BITÁCORA DE SOPORTE TÉCNICO Y MONITOREO

Se detectaron nuevas alertas durante la medición de un servidor.

Servidor: {nombre_servidor}
Identificador: {datos.servidor_id}

ALERTAS DETECTADAS:
{"".join(detalles_alertas)}

Se recomienda revisar el estado del servidor
y atender las condiciones reportadas.

Este mensaje fue generado automáticamente
por el sistema de monitoreo.
"""

            # Intenta enviar un único correo con todas las alertas.
            correo_enviado = enviar_correo_alerta(
                asunto=asunto,
                mensaje=mensaje,
            )

            # Solo marca las alertas como enviadas si el correo tuvo éxito.
            if correo_enviado:
                for alerta in alertas_nuevas:
                    alerta.correo_enviado = True

                # Guarda el estado de envío de cada alerta.
                db.commit()

                logger.info(
                    "Se enviaron %s alertas agrupadas del servidor %s.",
                    len(alertas_nuevas),
                    datos.servidor_id,
                )

            else:
                # Las alertas permanecen registradas como pendientes.
                logger.warning(
                    "No se pudo enviar el correo del servidor %s. "
                    "Las alertas permanecen pendientes.",
                    datos.servidor_id,
                )

        except Exception:
            # Un error de correo no debe afectar la medición ya guardada.
            db.rollback()

            logger.exception(
                "Error durante el envío o actualización del correo "
                "del servidor %s.",
                datos.servidor_id,
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
