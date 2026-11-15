
# Importamos las herramientas necesarias de FastAPI.
from fastapi import APIRouter, Depends, HTTPException

# Importamos la sesión de SQLAlchemy y el error de integridad.
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importamos la dependencia para conectarnos a PostgreSQL.
from app.database.dependencies import get_db

# Importamos los modelos necesarios.
from app.models.respaldo import Respaldo
from app.models.equipo import Equipo
from app.models.servidor import Servidor

# Importamos el esquema de validación.
from app.schemas.respaldo import RespaldoCreate

# Importamos el servicio que ejecuta los respaldos automáticos.
from app.services.respaldos_automaticos import ejecutar_respaldo_postgres


# ==========================================================
# CONFIGURACIÓN DEL ROUTER
# ==========================================================

# Creamos el router para administrar los respaldos.
router = APIRouter(
    prefix="/api/respaldos",
    tags=["Respaldos"]
)


# ==========================================================
# VALIDAR EQUIPO
# ==========================================================

def validar_equipo(equipo_id: int, db: Session):
    # Buscamos el equipo por su identificador.
    equipo = db.query(Equipo).filter(
        Equipo.id == equipo_id
    ).first()

    # Comprobamos que el equipo exista.
    if equipo is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el equipo seleccionado."
        )

    return equipo


# ==========================================================
# VALIDAR SERVIDOR
# ==========================================================

def validar_servidor(servidor_id: int, db: Session):
    # Buscamos el servidor por su identificador.
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id
    ).first()

    # Comprobamos que el servidor exista.
    if servidor is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el servidor seleccionado."
        )

    return servidor


# ==========================================================
# CONSULTAR TODOS LOS RESPALDOS
# ==========================================================

@router.get("/")
def obtener_respaldos(db: Session = Depends(get_db)):

    # Consultamos todos los registros de respaldos.
    respaldos = db.query(Respaldo).all()

    # Convertimos los registros a una lista de objetos JSON.
    return [
        {
            "id": respaldo.id,
            "equipo_id": respaldo.equipo_id,
            "servidor_id": respaldo.servidor_id,
            "fecha_hora": respaldo.fecha_hora,
            "tipo_respaldo": respaldo.tipo_respaldo,
            "tamanio_mb": respaldo.tamanio_mb,
            "resultado": respaldo.resultado,
            "dispositivo_externo": respaldo.dispositivo_externo,
            "ruta_destino": respaldo.ruta_destino,
            "detalles_error": respaldo.detalles_error,
        }
        for respaldo in respaldos
    ]


# ==========================================================
# REGISTRAR UN RESPALDO MANUALMENTE
# ==========================================================

@router.post("/")
def crear_respaldo(
    datos: RespaldoCreate,
    db: Session = Depends(get_db)
):

    # Validamos que el equipo exista.
    validar_equipo(datos.equipo_id, db)

    # Validamos el servidor cuando se proporciona uno.
    if datos.servidor_id is not None:
        validar_servidor(datos.servidor_id, db)

    # Construimos el registro con los datos recibidos.
    nuevo_respaldo = Respaldo(
        equipo_id=datos.equipo_id,
        servidor_id=datos.servidor_id,
        tipo_respaldo=datos.tipo_respaldo,
        tamanio_mb=datos.tamanio_mb,
        resultado=datos.resultado,
        dispositivo_externo=datos.dispositivo_externo,
        ruta_destino=datos.ruta_destino,
        detalles_error=datos.detalles_error,
    )

    try:
        # Agregamos el respaldo a la sesión.
        db.add(nuevo_respaldo)

        # Guardamos el registro en PostgreSQL.
        db.commit()

        # Recuperamos los datos guardados.
        db.refresh(nuevo_respaldo)

    except IntegrityError:
        # Revertimos los cambios si ocurre un error.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el respaldo. "
                "Verifica que los datos sean válidos."
            )
        )

    # Devolvemos los datos del respaldo registrado.
    return {
        "id": nuevo_respaldo.id,
        "equipo_id": nuevo_respaldo.equipo_id,
        "servidor_id": nuevo_respaldo.servidor_id,
        "fecha_hora": nuevo_respaldo.fecha_hora,
        "tipo_respaldo": nuevo_respaldo.tipo_respaldo,
        "tamanio_mb": nuevo_respaldo.tamanio_mb,
        "resultado": nuevo_respaldo.resultado,
        "dispositivo_externo": nuevo_respaldo.dispositivo_externo,
        "ruta_destino": nuevo_respaldo.ruta_destino,
        "detalles_error": nuevo_respaldo.detalles_error,
    }


# ==========================================================
# EJECUTAR UN RESPALDO AUTOMÁTICO DE POSTGRESQL
# ==========================================================

@router.post("/ejecutar")
def ejecutar_respaldo(
    equipo_id: int,
    servidor_id: int | None = None,
    db: Session = Depends(get_db)
):

    # Validamos que el equipo relacionado exista.
    validar_equipo(equipo_id, db)

    # Validamos el servidor cuando se proporciona uno.
    if servidor_id is not None:
        validar_servidor(servidor_id, db)

    try:
        # Ejecutamos el servicio que genera el archivo .backup.
        # El servicio también registra el resultado de la operación.
        respaldo = ejecutar_respaldo_postgres(
            db=db,
            equipo_id=equipo_id,
            servidor_id=servidor_id,
        )

    except Exception:
        # Revertimos la transacción si ocurre un error al registrar.
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Ocurrió un error al ejecutar o registrar "
                "el respaldo automático."
            )
        )

    # Devolvemos el resultado de la operación.
    return {
        "mensaje": (
            "Respaldo generado correctamente."
            if respaldo.resultado == "Exitoso"
            else "El respaldo no pudo completarse."
        ),
        "id": respaldo.id,
        "equipo_id": respaldo.equipo_id,
        "servidor_id": respaldo.servidor_id,
        "fecha_hora": respaldo.fecha_hora,
        "tipo_respaldo": respaldo.tipo_respaldo,
        "tamanio_mb": respaldo.tamanio_mb,
        "resultado": respaldo.resultado,
        "dispositivo_externo": respaldo.dispositivo_externo,
        "ruta_destino": respaldo.ruta_destino,
        "detalles_error": respaldo.detalles_error,
    }
