
import os
import shutil
import subprocess

from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.respaldo import Respaldo


# ============================================================
# CONFIGURACIÓN DEL SERVICIO DE RESPALDOS
# ============================================================

# Obtenemos la ruta principal del proyecto.
RUTA_PROYECTO = Path(__file__).resolve().parents[3]

# Cargamos explícitamente el archivo .env de la raíz del proyecto.
# override=True permite utilizar los valores definidos en ese archivo.
RUTA_ENV = RUTA_PROYECTO / ".env"
load_dotenv(dotenv_path=RUTA_ENV, override=True)

# Definimos dónde se guardarán los respaldos.
# Si BACKUP_DIR no existe en .env, utilizamos una carpeta local
# fuera de OneDrive.
RUTA_RESPALDOS = Path(
    os.getenv(
        "BACKUP_DIR",
        str(Path.home() / "BitacoraRespaldos")
    )
).expanduser()

# Tiempo máximo permitido para generar una copia (30 minutos).
TIEMPO_MAXIMO = 1800


# ============================================================
# OBTENER CONFIGURACIÓN DE POSTGRESQL
# ============================================================

def obtener_configuracion_bd():
    """
    Obtiene los datos de conexión desde las variables de entorno.
    Las contraseñas nunca se escriben directamente en el código.
    """

    configuracion = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    # Comprobamos que todas las variables necesarias existan.
    faltantes = [
        nombre
        for nombre, valor in configuracion.items()
        if not valor
    ]

    if faltantes:
        raise ValueError(
            "Faltan variables de configuración de PostgreSQL: "
            + ", ".join(faltantes)
        )

    return configuracion


# ============================================================
# EJECUTAR RESPALDO DE POSTGRESQL
# ============================================================

def ejecutar_respaldo_postgres(
    db: Session,
    equipo_id: int,
    servidor_id: int | None = None,
):
    """
    Genera una copia real de PostgreSQL mediante pg_dump
    y registra automáticamente el resultado en la bitácora.

    Parámetros:
    - db: sesión de conexión con SQLAlchemy.
    - equipo_id: equipo relacionado con la operación.
    - servidor_id: servidor relacionado, si corresponde.
    """

    # Inicializamos las variables de la operación.
    archivo_respaldo = None
    resultado = "Fallido"
    tamanio_mb = None
    detalles_error = None

    try:
        # Obtenemos los datos de conexión de PostgreSQL.
        configuracion = obtener_configuracion_bd()

        # Localizamos el ejecutable pg_dump.
        ejecutable = shutil.which("pg_dump")

        if not ejecutable:
            raise FileNotFoundError(
                "No se encontró pg_dump. "
                "Verifica la instalación de PostgreSQL."
            )

        # Creamos la carpeta de respaldos si no existe.
        RUTA_RESPALDOS.mkdir(parents=True, exist_ok=True)

        # Generamos un nombre único para evitar sobrescribir copias.
        fecha_archivo = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        nombre_archivo = (
            f"bitacora_soporte_{fecha_archivo}.backup"
        )

        archivo_respaldo = RUTA_RESPALDOS / nombre_archivo

        # Preparamos las variables de entorno para pg_dump.
        entorno = os.environ.copy()
        entorno["PGPASSWORD"] = configuracion["password"]

        # Construimos el comando para generar el respaldo.
        # El formato custom permite utilizar pg_restore posteriormente.
        comando = [
            ejecutable,
            "--host", configuracion["host"],
            "--port", configuracion["port"],
            "--username", configuracion["user"],
            "--dbname", configuracion["database"],
            "--format=custom",
            "--no-password",
            "--file", str(archivo_respaldo),
        ]

        # Ejecutamos pg_dump y esperamos a que termine.
        proceso = subprocess.run(
            comando,
            env=entorno,
            capture_output=True,
            text=True,
            timeout=TIEMPO_MAXIMO,
            check=False,
        )

        # Comprobamos si PostgreSQL reportó algún error.
        if proceso.returncode != 0:
            raise RuntimeError(
                proceso.stderr.strip()
                or "PostgreSQL no pudo completar el respaldo."
            )

        # Verificamos que el archivo exista y no esté vacío.
        if (
            not archivo_respaldo.exists()
            or archivo_respaldo.stat().st_size == 0
        ):
            raise RuntimeError(
                "El archivo de respaldo no se generó correctamente."
            )

        # Calculamos el tamaño del archivo en megabytes.
        tamanio_mb = round(
            archivo_respaldo.stat().st_size / (1024 * 1024),
            2,
        )

        # Indicamos que el respaldo se generó correctamente.
        resultado = "Exitoso"

    except Exception as error:
        # Guardamos la descripción del error ocurrido.
        detalles_error = str(error)

        # Eliminamos únicamente el archivo parcial de esta operación.
        # Nunca modificamos respaldos anteriores.
        if archivo_respaldo and archivo_respaldo.exists():
            try:
                archivo_respaldo.unlink()
            except OSError:
                detalles_error += (
                    " También ocurrió un error al eliminar "
                    "el archivo incompleto."
                )

        archivo_respaldo = None

    # ========================================================
    # REGISTRAR EL RESULTADO EN POSTGRESQL
    # ========================================================

    # Construimos el registro de la operación.
    nuevo_respaldo = Respaldo(
        equipo_id=equipo_id,
        servidor_id=servidor_id,
        fecha_hora=datetime.now(),
        tipo_respaldo="Completo",
        tamanio_mb=tamanio_mb,
        resultado=resultado,
        dispositivo_externo="Almacenamiento local",
        ruta_destino=(
            str(archivo_respaldo)
            if archivo_respaldo
            else str(RUTA_RESPALDOS)
        ),
        detalles_error=detalles_error,
    )

    # Guardamos el resultado en la tabla de respaldos.
    db.add(nuevo_respaldo)

    try:
        db.commit()
        db.refresh(nuevo_respaldo)

    except Exception:
        # Revertimos la transacción si falla el registro.
        db.rollback()
        raise

    # Devolvemos el registro generado.
    return nuevo_respaldo
