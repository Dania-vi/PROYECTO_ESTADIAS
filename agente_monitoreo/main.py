
# Permite trabajar con rutas y archivos del proyecto.
from pathlib import Path

# Permite localizar los módulos del backend.
import sys

# Permite controlar el intervalo entre mediciones.
import time

# Permite convertir las mediciones a formato JSON.
import json

# Permite enviar solicitudes HTTP a la API.
import requests


# Obtiene la carpeta principal del proyecto.
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent

# Agrega la carpeta backend a las rutas de búsqueda de Python.
sys.path.insert(0, str(CARPETA_PROYECTO / "backend"))

# Importa la configuración del agente.
from config import URL_API, SERVIDOR_ID, INTERVALO_SEGUNDOS

# Importa la función que recopila las métricas del equipo.
from app.services.monitoreo_servidor import obtener_metricas_servidor


# Dirección del endpoint que registra las métricas.
URL_METRICAS = f"{URL_API}/api/metricas-servidor/"

# Archivo local donde se conservarán las mediciones pendientes.
# Se creará automáticamente cuando sea necesario.
ARCHIVO_PENDIENTES = Path(__file__).resolve().parent / "metricas_pendientes.jsonl"


def guardar_pendiente(datos):
    """
    Guarda una medición en un archivo local para enviarla después.
    """

    # Abre el archivo en modo de agregar, sin borrar datos anteriores.
    with ARCHIVO_PENDIENTES.open("a", encoding="utf-8") as archivo:

        # Guarda una medición por línea para facilitar su recuperación.
        archivo.write(json.dumps(datos, ensure_ascii=False) + "\n")

    print("Métrica guardada localmente para enviarla después.")


def enviar_datos(datos):
    """
    Envía una medición a la API.

    Devuelve True si se guardó correctamente y False si no pudo enviarse.
    """

    try:
        # Envía la medición a FastAPI.
        respuesta = requests.post(
            URL_METRICAS,
            json=datos,
            timeout=10
        )

        # Comprueba si hubo un error en la respuesta HTTP.
        respuesta.raise_for_status()

        # Lee la respuesta con los datos del registro creado.
        resultado = respuesta.json()

        print("¡Métrica guardada correctamente!")
        print(f"ID de la medición: {resultado['id']}")
        print(f"Servidor asociado: {resultado['servidor_id']}")
        print(f"Fecha de registro: {resultado['fecha_hora']}")

        return True

    except requests.exceptions.HTTPError as error:
        # Los errores HTTP 4xx suelen indicar datos o configuración incorrectos.
        # Los errores 5xx indican un problema del lado del servidor.
        codigo = error.response.status_code

        if codigo >= 500:
            print(f"Error del servidor API ({codigo}).")
            return False

        # No se guarda automáticamente un error 4xx en la cola,
        # porque repetir la misma solicitud no suele solucionar el problema.
        print(f"La API rechazó la medición (HTTP {codigo}): {error}")
        return None

    except requests.exceptions.RequestException as error:
        # Si no se logra conectar con la API, se podrá guardar la medición
        # localmente para intentar enviarla en otra ocasión.
        print(f"No se pudo conectar con la API: {error}")
        return False


def reenviar_pendientes():
    """
    Intenta enviar las mediciones que quedaron pendientes.

    Conserva en el archivo las mediciones que todavía no se hayan enviado.
    """

    # Si no existe el archivo, no hay mediciones pendientes.
    if not ARCHIVO_PENDIENTES.exists():
        return

    # Lee las mediciones pendientes, una por cada línea.
    with ARCHIVO_PENDIENTES.open("r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    # Si el archivo está vacío, no hay nada que reenviar.
    if not lineas:
        return

    print(f"Hay {len(lineas)} medición(es) pendiente(s). Intentando reenviar...")

    # Almacena las mediciones que todavía no puedan enviarse.
    pendientes_restantes = []

    # Procesa las mediciones en el orden en que fueron guardadas.
    for indice, linea in enumerate(lineas):
        try:
            # Convierte la línea JSON nuevamente en un diccionario.
            datos = json.loads(linea)

        except json.JSONDecodeError:
            # Conserva la línea si no se puede interpretar, para no descartarla.
            pendientes_restantes.append(linea)
            print("Hay una línea pendiente que no se pudo interpretar.")
            continue

        # Intenta enviar la medición a la API.
        resultado = enviar_datos(datos)

        if resultado is True:
            # La API confirmó el registro; ya no es necesario conservarlo.
            continue

        # Si la API no está disponible, conserva esta medición y las siguientes.
        pendientes_restantes.extend(lineas[indice:])
        break

    # Reescribe el archivo únicamente con las mediciones que siguen pendientes.
    # Si todas se enviaron, el archivo queda vacío.
    with ARCHIVO_PENDIENTES.open("w", encoding="utf-8") as archivo:
        archivo.writelines(pendientes_restantes)

    if pendientes_restantes:
        print(f"Siguen pendientes {len(pendientes_restantes)} línea(s).")
    else:
        print("Todas las mediciones pendientes fueron enviadas.")


def ejecutar_agente():
    """
    Recopila métricas periódicamente y las envía a la API.
    """

    # Obtiene el nombre del equipo para mostrarlo al iniciar.
    datos_equipo = obtener_metricas_servidor()

    print("Agente de monitoreo iniciado.")
    print(f"Equipo: {datos_equipo['nombre_equipo']}")
    print(f"Servidor de prueba asociado: {SERVIDOR_ID}")
    print(f"API de destino: {URL_METRICAS}")
    print(f"Intervalo: {INTERVALO_SEGUNDOS} segundos.")
    print("Presiona Ctrl + C para detenerlo.\n")

    try:
        # Repite el monitoreo hasta que se detenga manualmente.
        while True:

            # Primero intenta enviar las mediciones guardadas anteriormente.
            reenviar_pendientes()

            # Recopila las métricas actuales del equipo.
            metricas = obtener_metricas_servidor()

            # Prepara los datos con los nombres que espera el backend.
            datos = {
                "servidor_id": SERVIDOR_ID,
                "cpu_uso_porcentaje": metricas["cpu_uso_porcentaje"],
                "ram_uso_porcentaje": metricas["ram_uso_porcentaje"],
                "ram_usada_mb": metricas["ram_usada_mb"],
                "disco_uso_porcentaje": metricas["disco_uso_porcentaje"],
                "disco_libre_gb": metricas["disco_libre_gb"],
                "internet_activo": metricas["internet_activo"],
                "latencia_ms": metricas["latencia_ms"],
            }

            # Muestra las métricas recopiladas en la terminal.
            print("\n----- MÉTRICAS DEL EQUIPO -----")

            for nombre, valor in metricas.items():
                print(f"{nombre}: {valor}")

            # Intenta enviar la medición recién recopilada.
            resultado = enviar_datos(datos)

            if resultado is False:
                # Si falla la conexión o la API, conserva la medición localmente.
                guardar_pendiente(datos)

            print("--------------------------------\n")

            # Espera antes de recopilar la siguiente medición.
            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        # Finaliza el agente de forma controlada.
        print("\nAgente de monitoreo detenido.")


# Inicia el agente al ejecutar directamente este archivo.
if __name__ == "__main__":
    ejecutar_agente()
