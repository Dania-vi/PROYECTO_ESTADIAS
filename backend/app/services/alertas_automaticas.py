
# Importa la sesión para consultar y guardar información en PostgreSQL.
from sqlalchemy.orm import Session

# Importa el modelo de las alertas.
from app.models.alerta import Alerta


def revisar_metricas_y_generar_alertas(
    db: Session,
    servidor_id: int,
    metricas: dict,
    metricas_anteriores: dict | None = None,
):
    """
    Revisa las métricas y prepara alertas cuando se superan los límites.

    Compara las mediciones actuales con las anteriores para evitar
    repetir una alerta mientras el mismo problema continúa activo.
    """

    # Si no hay una medición anterior, se considera la primera revisión.
    if metricas_anteriores is None:
        metricas_anteriores = {}

    # Aquí se almacenarán las alertas que deban crearse.
    alertas_generadas = []

    # Obtiene los valores actuales y anteriores de CPU, RAM y disco.
    cpu = metricas.get("cpu_uso_porcentaje")
    cpu_anterior = metricas_anteriores.get("cpu_uso_porcentaje")

    ram = metricas.get("ram_uso_porcentaje")
    ram_anterior = metricas_anteriores.get("ram_uso_porcentaje")

    disco = metricas.get("disco_uso_porcentaje")
    disco_anterior = metricas_anteriores.get("disco_uso_porcentaje")

    internet = metricas.get("internet_activo")
    internet_anterior = metricas_anteriores.get("internet_activo")

    # Comprueba si la CPU acaba de superar el umbral del 85 %.
    if (
        cpu is not None
        and cpu > 85
        and (cpu_anterior is None or cpu_anterior <= 85)
    ):
        alertas_generadas.append({
            "metrica_afectada": "CPU",
            "valor_registrado": f"{cpu}%",
            "nivel_alerta": "Advertencia",
            "mensaje": f"El uso de CPU superó el umbral del 85 %: {cpu}%.",
        })

    # Comprueba si la RAM acaba de superar el umbral del 90 %.
    if (
        ram is not None
        and ram > 90
        and (ram_anterior is None or ram_anterior <= 90)
    ):
        alertas_generadas.append({
            "metrica_afectada": "RAM",
            "valor_registrado": f"{ram}%",
            "nivel_alerta": "Advertencia",
            "mensaje": f"El uso de RAM superó el umbral del 90 %: {ram}%.",
        })

    # Comprueba si el disco acaba de superar el 90 % de uso.
    # Esto equivale a tener menos del 10 % de espacio libre.
    if (
        disco is not None
        and disco > 90
        and (disco_anterior is None or disco_anterior <= 90)
    ):
        # Calcula el porcentaje libre, incluso si el disco está al 100 %.
        espacio_libre = max(0, 100 - disco)

        alertas_generadas.append({
            "metrica_afectada": "Disco",
            "valor_registrado": f"{espacio_libre:.2f}% libre",
            "nivel_alerta": "Advertencia",
            "mensaje": "El espacio libre en disco es inferior al 10 %.",
        })

    # Genera una alerta cuando se pierde la conexión a Internet.
    if internet is False and internet_anterior is not False:
        alertas_generadas.append({
            "metrica_afectada": "Internet",
            "valor_registrado": "Sin conexión",
            "nivel_alerta": "Problema",
            "mensaje": "No se pudo comprobar la conexión a Internet.",
        })

    # Convierte los datos de cada alerta en registros del modelo.
    objetos_alerta = [
        Alerta(
            servidor_id=servidor_id,
            respaldo_id=None,
            tipo_alerta="Monitoreo",
            metrica_afectada=datos["metrica_afectada"],
            valor_registrado=datos["valor_registrado"],
            nivel_alerta=datos["nivel_alerta"],
            mensaje=datos["mensaje"],
            correo_enviado=False,
        )
        for datos in alertas_generadas
    ]

    # Añade las alertas a la transacción actual.
    # El endpoint será responsable de confirmar los cambios con commit().
    if objetos_alerta:
        db.add_all(objetos_alerta)
        db.flush()

    # Devuelve las alertas preparadas para guardarse.
    return objetos_alerta
