
# Permite acceder a la sesión de PostgreSQL.
from sqlalchemy.orm import Session

# Importa el modelo que representa la tabla de métricas.
from app.models.metrica_servidor import MetricaServidor

# Importa el modelo de los servidores registrados.
from app.models.servidor import Servidor

# Importa la función que recopila las métricas del equipo.
from app.services.monitoreo_servidor import obtener_metricas_servidor


def registrar_metricas(
    db: Session,
    servidor_id: int
) -> dict:
    """
    Obtiene las métricas del equipo local y las guarda en PostgreSQL
    asociándolas al servidor indicado.
    """

    # Comprueba que el servidor exista antes de guardar la medición.
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id
    ).first()

    if servidor is None:
        raise ValueError(
            f"No existe un servidor registrado con ID {servidor_id}."
        )

    # Recopila las métricas actuales del equipo donde corre el servicio.
    datos = obtener_metricas_servidor()

    # Crea una medición usando los campos definidos en el modelo.
    metrica = MetricaServidor(
        servidor_id=servidor_id,
        cpu_uso_porcentaje=datos["cpu_uso_porcentaje"],
        ram_uso_porcentaje=datos["ram_uso_porcentaje"],
        ram_usada_mb=datos["ram_usada_mb"],
        disco_uso_porcentaje=datos["disco_uso_porcentaje"],
        disco_libre_gb=datos["disco_libre_gb"],
        internet_activo=datos["internet_activo"],
        latencia_ms=datos["latencia_ms"],
    )

    try:
        # Agrega la medición y actualiza la última conexión registrada.
        db.add(metrica)

        from datetime import datetime
        servidor.ultima_conexion = datetime.now()

        # Guarda ambos cambios en una sola transacción.
        db.commit()

        # Recupera los valores generados por PostgreSQL.
        db.refresh(metrica)

    except Exception:
        # Revierte los cambios si ocurre algún error en el guardado.
        db.rollback()
        raise

    # Devuelve los datos que quedaron guardados.
    return {
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
