
# Importamos las herramientas necesarias de FastAPI.
from fastapi import APIRouter, Depends, HTTPException

# Importamos la sesión de SQLAlchemy.
from sqlalchemy.orm import Session

# Importamos la excepción para manejar errores de integridad.
from sqlalchemy.exc import IntegrityError

# Importamos la dependencia para conectarnos a PostgreSQL.
from app.database.dependencies import get_db

# Importamos los modelos de técnicos, mantenimientos e historial.
from app.models.tecnico import Tecnico
from app.models.mantenimiento import Mantenimiento
from app.models.historial import Historial

# Importamos los esquemas para crear y actualizar técnicos.
from app.schemas.tecnico import TecnicoCreate, TecnicoUpdate


# Creamos el router para administrar los técnicos.
router = APIRouter(
    prefix="/api/tecnicos",
    tags=["Técnicos"]
)


# ==========================================================
# CONSULTAR TODOS LOS TÉCNICOS
# ==========================================================

@router.get("/")
def obtener_tecnicos(db: Session = Depends(get_db)):

    # Consultamos todos los técnicos registrados.
    tecnicos = db.query(Tecnico).all()

    # Convertimos los registros en una lista de objetos JSON.
    return [
        {
            "id": tecnico.id,
            "nombre": tecnico.nombre,
            "correo": tecnico.correo,
            "telefono": tecnico.telefono,
            "activo": tecnico.activo
        }
        for tecnico in tecnicos
    ]


# ==========================================================
# REGISTRAR UN TÉCNICO NUEVO
# ==========================================================

@router.post("/")
def crear_tecnico(
    datos: TecnicoCreate,
    db: Session = Depends(get_db)
):

    # Creamos el objeto con los datos recibidos.
    nuevo_tecnico = Tecnico(
        nombre=datos.nombre,
        correo=datos.correo,
        telefono=datos.telefono,
        activo=datos.activo
    )

    try:
        # Agregamos el técnico a la sesión de SQLAlchemy.
        db.add(nuevo_tecnico)

        # Enviamos el INSERT a PostgreSQL para obtener el ID generado.
        # Todavía no confirmamos la transacción.
        db.flush()

        # Creamos el evento que documenta el registro del técnico.
        evento = Historial(
            modulo="tecnicos",
            accion="creacion",
            descripcion=(
                f"Se registró el técnico '{nuevo_tecnico.nombre}'."
            ),
            entidad="tecnico",
            entidad_id=nuevo_tecnico.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma transacción.
        db.add(evento)

        # Confirmamos juntos el técnico y su evento de historial.
        db.commit()

        # Recuperamos los datos guardados.
        db.refresh(nuevo_tecnico)

    except IntegrityError:
        # Revertimos ambos registros si ocurre un error de integridad.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="No se pudo registrar el técnico. Verifica que los datos sean válidos."
        )

    # Devolvemos los datos del técnico registrado.
    return {
        "id": nuevo_tecnico.id,
        "nombre": nuevo_tecnico.nombre,
        "correo": nuevo_tecnico.correo,
        "telefono": nuevo_tecnico.telefono,
        "activo": nuevo_tecnico.activo
    }


# ==========================================================
# ACTUALIZAR UN TÉCNICO
# ==========================================================

@router.put("/{tecnico_id}")
def actualizar_tecnico(
    tecnico_id: int,
    datos: TecnicoUpdate,
    db: Session = Depends(get_db)
):

    # Buscamos el técnico mediante su identificador.
    tecnico = db.query(Tecnico).filter(
        Tecnico.id == tecnico_id
    ).first()

    # Verificamos que el técnico exista.
    if tecnico is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el técnico solicitado."
        )

    # Obtenemos únicamente los campos enviados.
    datos_actualizados = datos.model_dump(exclude_unset=True)

    # Evitamos realizar una actualización vacía.
    if not datos_actualizados:
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un campo para actualizar."
        )

    # Evitamos asignar un nombre nulo al técnico.
    if "nombre" in datos_actualizados and datos_actualizados["nombre"] is None:
        raise HTTPException(
            status_code=400,
            detail="El nombre del técnico no puede estar vacío."
        )

    # Guardamos el nombre anterior antes de aplicar los cambios.
    nombre_anterior = tecnico.nombre

    # Actualizamos los campos proporcionados.
    for campo, valor in datos_actualizados.items():
        setattr(tecnico, campo, valor)

    try:
        # Creamos el evento que documenta la actualización.
        evento = Historial(
            modulo="tecnicos",
            accion="actualizacion",
            descripcion=(
                f"Se actualizó el técnico '{nombre_anterior}' "
                f"(ID {tecnico.id}). "
                f"Nombre actual: '{tecnico.nombre}'."
            ),
            entidad="tecnico",
            entidad_id=tecnico.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma transacción.
        db.add(evento)

        # Confirmamos juntos la actualización y su evento.
        db.commit()

        # Recuperamos los datos actualizados.
        db.refresh(tecnico)

    except IntegrityError:
        # Revertimos los cambios si ocurre un error de integridad.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="No se pudo actualizar el técnico. Verifica que los datos sean válidos."
        )

    # Devolvemos la información actualizada.
    return {
        "id": tecnico.id,
        "nombre": tecnico.nombre,
        "correo": tecnico.correo,
        "telefono": tecnico.telefono,
        "activo": tecnico.activo
    }


# ==========================================================
# ELIMINAR UN TÉCNICO DE FORMA CONTROLADA
# ==========================================================

@router.delete("/{tecnico_id}")
def eliminar_tecnico(
    tecnico_id: int,
    db: Session = Depends(get_db)
):

    # Buscamos el técnico que se desea eliminar.
    tecnico = db.query(Tecnico).filter(
        Tecnico.id == tecnico_id
    ).first()

    # Si no existe, devolvemos un error 404.
    if tecnico is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el técnico solicitado."
        )

    # Contamos los mantenimientos relacionados con el técnico.
    mantenimientos_asociados = db.query(Mantenimiento).filter(
        Mantenimiento.tecnico_id == tecnico_id
    ).count()

    # Si tiene mantenimientos, bloqueamos la eliminación.
    if mantenimientos_asociados > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar el técnico porque tiene "
                f"{mantenimientos_asociados} mantenimiento(s) asociado(s). "
                "Conserva su historial o desactiva al técnico."
            )
        )

    try:
        # Guardamos el nombre antes de eliminar el registro.
        nombre_tecnico = tecnico.nombre

        # Creamos el evento que documenta la eliminación.
        evento = Historial(
            modulo="tecnicos",
            accion="eliminacion",
            descripcion=(
                f"Se eliminó el técnico '{nombre_tecnico}' "
                f"(ID {tecnico.id})."
            ),
            entidad="tecnico",
            entidad_id=tecnico.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la sesión.
        db.add(evento)

        # Eliminamos el técnico.
        db.delete(tecnico)

        # Confirmamos juntos el evento y la eliminación.
        db.commit()

    except IntegrityError:
        # Revertimos los cambios si existe otra restricción relacionada.
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el técnico porque existen registros relacionados."
        )

    # Confirmamos que la eliminación se realizó correctamente.
    return {
        "mensaje": "Técnico eliminado correctamente.",
        "id": tecnico_id
    }
