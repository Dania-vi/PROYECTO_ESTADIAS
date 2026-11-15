
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.servidor import Servidor
from app.models.historial import Historial
from app.schemas.servidor import ServidorCreate, ServidorUpdate


# Define las rutas de la API relacionadas con los servidores.
router = APIRouter(
    prefix="/api/servidores",
    tags=["Servidores"]
)


# Consulta todos los servidores registrados en PostgreSQL.
@router.get("/")
def obtener_servidores(db: Session = Depends(get_db)):
    servidores = db.query(Servidor).all()

    # Convierte los registros en una lista de objetos JSON.
    return [
        {
            "id": servidor.id,
            "nombre_host": servidor.nombre_host,
            "direccion_ip": servidor.direccion_ip,
            "sistema_operativo": servidor.sistema_operativo,
            "estado_actual": servidor.estado_actual,
            "ultima_conexion": servidor.ultima_conexion,
        }
        for servidor in servidores
    ]


# Registra un servidor nuevo en la base de datos.
@router.post("/")
def crear_servidor(
    datos: ServidorCreate,
    db: Session = Depends(get_db)
):
    # Construye el servidor con los datos recibidos.
    nuevo_servidor = Servidor(
        nombre_host=datos.nombre_host,
        direccion_ip=datos.direccion_ip,
        sistema_operativo=datos.sistema_operativo,
        estado_actual=datos.estado_actual,
        ultima_conexion=None,
    )

    db.add(nuevo_servidor)

    try:
        # Obtiene el ID del servidor sin confirmar todavía la transacción.
        db.flush()

        # Prepara el movimiento automático del historial.
        nuevo_historial = Historial(
            modulo="servidores",
            accion="creacion",
            descripcion=(
                f"Se registró el servidor {nuevo_servidor.nombre_host} "
                f"con dirección IP {nuevo_servidor.direccion_ip}."
            ),
            entidad="servidor",
            entidad_id=nuevo_servidor.id,
            usuario="Administrador",
        )

        db.add(nuevo_historial)

        # Guarda el servidor y su movimiento en una sola transacción.
        db.commit()
        db.refresh(nuevo_servidor)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el servidor. "
                "Verifica que los datos sean válidos."
            ),
        )

    return {
        "id": nuevo_servidor.id,
        "nombre_host": nuevo_servidor.nombre_host,
        "direccion_ip": nuevo_servidor.direccion_ip,
        "sistema_operativo": nuevo_servidor.sistema_operativo,
        "estado_actual": nuevo_servidor.estado_actual,
        "ultima_conexion": nuevo_servidor.ultima_conexion,
    }


# Actualiza la información de un servidor existente.
@router.put("/{servidor_id}")
def actualizar_servidor(
    servidor_id: int,
    datos: ServidorUpdate,
    db: Session = Depends(get_db)
):
    # Busca el servidor por su identificador.
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id
    ).first()

    # Si no existe, devuelve un error 404.
    if not servidor:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el servidor que deseas actualizar."
        )

    try:
        # Actualiza los campos permitidos con los datos recibidos.
        servidor.nombre_host = datos.nombre_host
        servidor.direccion_ip = datos.direccion_ip
        servidor.sistema_operativo = datos.sistema_operativo
        servidor.estado_actual = datos.estado_actual

        # Registra la actualización en el historial.
        nuevo_historial = Historial(
            modulo="servidores",
            accion="actualizacion",
            descripcion=(
                f"Se actualizó el servidor ID {servidor_id} "
                f"({servidor.nombre_host})."
            ),
            entidad="servidor",
            entidad_id=servidor.id,
            usuario="Administrador",
        )

        db.add(nuevo_historial)

        # Guarda la actualización y el historial juntos.
        db.commit()
        db.refresh(servidor)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se pudo actualizar el servidor. Verifica los datos."
        )

    return {
        "id": servidor.id,
        "nombre_host": servidor.nombre_host,
        "direccion_ip": servidor.direccion_ip,
        "sistema_operativo": servidor.sistema_operativo,
        "estado_actual": servidor.estado_actual,
        "ultima_conexion": servidor.ultima_conexion,
        "mensaje": "El servidor se actualizó correctamente."
    }


# Elimina un servidor existente.
@router.delete("/{servidor_id}")
def eliminar_servidor(
    servidor_id: int,
    db: Session = Depends(get_db)
):
    # Busca el servidor que se desea eliminar.
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id
    ).first()

    # Si no existe, devuelve un error 404.
    if not servidor:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el servidor que deseas eliminar."
        )

    try:
        # Conserva los datos necesarios antes de eliminar el servidor.
        nombre_host = servidor.nombre_host
        direccion_ip = servidor.direccion_ip

        # Registra la eliminación antes de borrar el servidor.
        nuevo_historial = Historial(
            modulo="servidores",
            accion="eliminacion",
            descripcion=(
                f"Se eliminó el servidor ID {servidor_id} "
                f"({nombre_host}), con dirección IP {direccion_ip}."
            ),
            entidad="servidor",
            entidad_id=servidor_id,
            usuario="Administrador",
        )

        db.add(nuevo_historial)

        # Elimina el servidor de PostgreSQL.
        db.delete(servidor)

        # Guarda la eliminación y el historial en una sola transacción.
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo eliminar el servidor. "
                "Verifica si tiene registros relacionados."
            ),
        )

    return {
        "mensaje": "El servidor se eliminó correctamente.",
        "id": servidor_id
    }
