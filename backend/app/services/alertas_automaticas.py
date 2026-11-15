
# Permite leer las variables de configuración del sistema.
import os

# Carga las variables definidas en el archivo .env.
from dotenv import load_dotenv

# Importa la sesión para consultar y guardar información en PostgreSQL.
from sqlalchemy.orm import Session

# Importa el modelo de las alertas.
from app.models.alerta import Alerta


# Carga las variables de entorno del proyecto.
load_dotenv()


# Obtiene los umbrales de advertencia desde el archivo .env.
# Si alguna variable no existe, utiliza el valor predeterminado.
UMBRAL_CPU = float(os.getenv("ALERT_CPU", "70"))
UMBRAL_RAM = float(os.getenv("ALERT_RAM", "80"))
UMBRAL_DISCO = float(os.getenv("ALERT_DISK", "80"))

# Define el umbral crítico para las tres métricas.
UMBRAL_PROBLEMA = 90


def obtener_nivel_alerta(
    valor_actual: float | None,
    umbral_advertencia: float,
    umbral_problema: float = UMBRAL_PROBLEMA,
):
    """
    Determina el nivel de alerta según el valor de una métrica.

    Devuelve:
    - None si el valor está dentro del rango normal.
    - Advertencia si supera el umbral de advertencia.
    - Problema si supera el umbral crítico.
    """

    # Si no existe un valor, no se genera una clasificación.
    if valor_actual is None:
        return None

    # Comprueba primero si se alcanzó el nivel crítico.
    if valor_actual > umbral_problema:
        return "Problema"

    # Comprueba si se superó el umbral de advertencia.
    if valor_actual > umbral_advertencia:
        return "Advertencia"

    # Si no supera ningún límite, el estado es normal.
    return None


def revisar_metricas_y_generar_alertas(
    db: Session,
    servidor_id: int,
    metricas: dict,
    metricas_anteriores: dict | None = None,
):
    """
    Revisa las métricas actuales y genera alertas cuando cambia su nivel.

    Compara las mediciones actuales con las anteriores para evitar
    repetir alertas mientras una misma condición continúa activa.
    """

    # Si no hay una medición anterior, se considera la primera revisión.
    if metricas_anteriores is None:
        metricas_anteriores = {}

    # Aquí se almacenarán los datos de las alertas que deben generarse.
    alertas_generadas = []

    # Obtiene los valores actuales y anteriores de las métricas.
    cpu = metricas.get("cpu_uso_porcentaje")
    cpu_anterior = metricas_anteriores.get("cpu_uso_porcentaje")

    ram = metricas.get("ram_uso_porcentaje")
    ram_anterior = metricas_anteriores.get("ram_uso_porcentaje")

    disco = metricas.get("disco_uso_porcentaje")
    disco_anterior = metricas_anteriores.get("disco_uso_porcentaje")

    internet = metricas.get("internet_activo")
    internet_anterior = metricas_anteriores.get("internet_activo")

    # Clasifica el nivel actual y anterior de cada métrica.
    nivel_cpu = obtener_nivel_alerta(cpu, UMBRAL_CPU)
    nivel_cpu_anterior = obtener_nivel_alerta(cpu_anterior, UMBRAL_CPU)

    nivel_ram = obtener_nivel_alerta(ram, UMBRAL_RAM)
    nivel_ram_anterior = obtener_nivel_alerta(ram_anterior, UMBRAL_RAM)

    nivel_disco = obtener_nivel_alerta(disco, UMBRAL_DISCO)
    nivel_disco_anterior = obtener_nivel_alerta(
        disco_anterior,
        UMBRAL_DISCO
    )

    # Comprueba si la CPU cambió a Advertencia o Problema.
    if nivel_cpu is not None and nivel_cpu != nivel_cpu_anterior:
        alertas_generadas.append({
            "metrica_afectada": "CPU",
            "valor_registrado": f"{cpu}%",
            "nivel_alerta": nivel_cpu,
            "mensaje": (
                f"El uso de CPU alcanzó el nivel {nivel_cpu}: "
                f"{cpu}%. Umbral de advertencia: {UMBRAL_CPU}%."
            ),
        })

    # Comprueba si la RAM cambió a Advertencia o Problema.
    if nivel_ram is not None and nivel_ram != nivel_ram_anterior:
        alertas_generadas.append({
            "metrica_afectada": "RAM",
            "valor_registrado": f"{ram}%",
            "nivel_alerta": nivel_ram,
            "mensaje": (
                f"El uso de RAM alcanzó el nivel {nivel_ram}: "
                f"{ram}%. Umbral de advertencia: {UMBRAL_RAM}%."
            ),
        })

    # Comprueba si el disco cambió a Advertencia o Problema.
    if nivel_disco is not None and nivel_disco != nivel_disco_anterior:

        # Calcula el porcentaje de espacio libre.
        espacio_libre = max(0, 100 - disco)

        alertas_generadas.append({
            "metrica_afectada": "Disco",
            "valor_registrado": f"{espacio_libre:.2f}% libre",
            "nivel_alerta": nivel_disco,
            "mensaje": (
                f"El uso del disco alcanzó el nivel {nivel_disco}: "
                f"{disco}%. Espacio libre: {espacio_libre:.2f}%."
            ),
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
