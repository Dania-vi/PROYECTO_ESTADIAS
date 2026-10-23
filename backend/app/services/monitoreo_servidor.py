
# Permite identificar el sistema operativo y el nombre del equipo.
import platform

# Permite obtener información de CPU, memoria RAM y disco.
import psutil

# Permite medir la latencia de una conexión de red.
import socket
import time


def obtener_metricas_servidor():
    """
    Obtiene las métricas actuales del equipo donde se ejecuta el servicio.

    Por ahora se utiliza la computadora local para realizar las pruebas.
    """

    # Calcula el uso de CPU durante un intervalo de un segundo.
    uso_cpu = psutil.cpu_percent(interval=1)

    # Obtiene información sobre el uso de memoria RAM.
    memoria = psutil.virtual_memory()

    # Consulta el espacio disponible en la unidad principal.
    # En Windows se utiliza C: y en Linux se utiliza la raíz /.
    unidad = "C:\\" if platform.system() == "Windows" else "/"
    disco = psutil.disk_usage(unidad)

    # Inicializa los datos de conectividad.
    internet_disponible = False
    latencia_ms = None

    # Intenta conectarse a un servidor DNS público para comprobar
    # la conectividad y medir el tiempo de respuesta.
    try:
        inicio = time.perf_counter()

        with socket.create_connection(("1.1.1.1", 53), timeout=3):
            fin = time.perf_counter()

        # Convierte la duración de la conexión a milisegundos.
        latencia_ms = round((fin - inicio) * 1000)
        internet_disponible = True

    except OSError:
        # Si no se puede establecer la conexión, conserva los valores
        # que indican que no se pudo comprobar el acceso a Internet.
        internet_disponible = False
        latencia_ms = None

    # Devuelve los datos con los nombres que utiliza el proyecto.
    return {
        "nombre_equipo": platform.node(),
        "sistema_operativo": platform.system(),
        "cpu_uso_porcentaje": uso_cpu,
        "ram_uso_porcentaje": memoria.percent,
        "ram_usada_mb": round(memoria.used / (1024 ** 2), 2),
        "disco_uso_porcentaje": disco.percent,
        "disco_libre_gb": round(disco.free / (1024 ** 3), 2),
        "internet_activo": internet_disponible,
        "latencia_ms": latencia_ms,
    }
