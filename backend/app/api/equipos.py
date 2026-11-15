
# Importamos las herramientas necesarias de FastAPI.
from fastapi import APIRouter, Depends, HTTPException

# Importamos la sesión de SQLAlchemy.
from sqlalchemy.orm import Session

# Importamos la excepción para manejar errores de integridad.
from sqlalchemy.exc import IntegrityError

# Importamos la dependencia para conectarnos a PostgreSQL.
from app.database.dependencies import get_db

# Importamos los modelos de equipos, sucursales, mantenimientos,
# respaldos e historial.
from app.models.equipo import Equipo
from app.models.sucursal import Sucursal
from app.models.mantenimiento import Mantenimiento
from app.models.respaldo import Respaldo
from app.models.historial import Historial

# Importamos los esquemas para crear y actualizar equipos.
from app.schemas.equipo import EquipoCreate, EquipoUpdate


# Creamos el router para administrar los equipos.
router = APIRouter(
    prefix="/api/equipos",
    tags=["Equipos"]
)


# ==========================================================
# CONSULTAR TODOS LOS EQUIPOS
# ==========================================================

@router.get("/")
def obtener_equipos(db: Session = Depends(get_db)):

    # Consultamos todos los equipos registrados.
    equipos = db.query(Equipo).all()

    # Convertimos los registros en una lista de objetos JSON.
    return [
        {
            "id": equipo.id,
            "sucursal_id": equipo.sucursal_id,
            "nombre": equipo.nombre,
            "tipo_equipo": equipo.tipo_equipo,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "numero_serie": equipo.numero_serie,
            "estado": equipo.estado
        }
        for equipo in equipos
    ]


# ==========================================================
# REGISTRAR UN EQUIPO NUEVO
# ==========================================================

@router.post("/")
def crear_equipo(
    datos: EquipoCreate,
    db: Session = Depends(get_db)
):

    # Buscamos la sucursal seleccionada.
    sucursal = db.query(Sucursal).filter(
        Sucursal.id == datos.sucursal_id
    ).first()

    # Verificamos que la sucursal exista.
    if sucursal is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la sucursal seleccionada."
        )

    # Impedimos registrar equipos en sucursales inactivas.
    if not sucursal.activo:
        raise HTTPException(
            status_code=400,
            detail="No se pueden registrar equipos en una sucursal inactiva."
        )

    # Eliminamos espacios al inicio y al final del nombre.
    nombre_equipo = datos.nombre.strip()

    # Verificamos que el nombre no esté vacío.
    if not nombre_equipo:
        raise HTTPException(
            status_code=400,
            detail="El nombre del equipo es obligatorio."
        )

    # Creamos el objeto con los datos recibidos.
    nuevo_equipo = Equipo(
        sucursal_id=datos.sucursal_id,
        nombre=nombre_equipo,
        tipo_equipo=datos.tipo_equipo,
        marca=datos.marca,
        modelo=datos.modelo,
        numero_serie=datos.numero_serie,
        estado=datos.estado
    )

    try:
        # Agregamos el equipo a la sesión de SQLAlchemy.
        db.add(nuevo_equipo)

        # Ejecutamos el INSERT sin confirmar la transacción.
        # Esto permite obtener el ID generado para el equipo.
        db.flush()

        # Creamos el evento que documenta el registro.
        nuevo_historial = Historial(
            modulo="equipos",
            accion="creacion",
            descripcion=(
                f"Se registró el equipo '{nuevo_equipo.nombre}' "
                f"en la sucursal ID {nuevo_equipo.sucursal_id}."
            ),
            entidad="equipo",
            entidad_id=nuevo_equipo.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma sesión.
        db.add(nuevo_historial)

        # Confirmamos el equipo y su historial juntos.
        db.commit()

        # Recuperamos los datos guardados.
        db.refresh(nuevo_equipo)

    except IntegrityError:
        # Revertimos ambas operaciones si ocurre un error.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el equipo. "
                "Verifica que la sucursal exista y que los datos sean válidos."
            )
        )

    # Devolvemos los datos del equipo registrado.
    return {
        "id": nuevo_equipo.id,
        "sucursal_id": nuevo_equipo.sucursal_id,
        "nombre": nuevo_equipo.nombre,
        "tipo_equipo": nuevo_equipo.tipo_equipo,
        "marca": nuevo_equipo.marca,
        "modelo": nuevo_equipo.modelo,
        "numero_serie": nuevo_equipo.numero_serie,
        "estado": nuevo_equipo.estado
    }


# ==========================================================
# ACTUALIZAR UN EQUIPO
# ==========================================================

@router.put("/{equipo_id}")
def actualizar_equipo(
    equipo_id: int,
    datos: EquipoUpdate,
    db: Session = Depends(get_db)
):

    # Buscamos el equipo mediante su identificador.
    equipo = db.query(Equipo).filter(
        Equipo.id == equipo_id
    ).first()

    # Verificamos que el equipo exista.
    if equipo is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el equipo solicitado."
        )

    # Obtenemos solamente los campos enviados en la petición.
    datos_actualizados = datos.model_dump(exclude_unset=True)

    # Evitamos realizar una actualización vacía.
    if not datos_actualizados:
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un campo para actualizar."
        )

    # Evitamos asignar un nombre nulo al equipo.
    if "nombre" in datos_actualizados:
        if datos_actualizados["nombre"] is None:
            raise HTTPException(
                status_code=400,
                detail="El nombre del equipo no puede estar vacío."
            )

        # Eliminamos espacios al inicio y al final.
        nombre_limpio = datos_actualizados["nombre"].strip()

        # Impedimos guardar un nombre compuesto únicamente por espacios.
        if not nombre_limpio:
            raise HTTPException(
                status_code=400,
                detail="El nombre del equipo no puede estar vacío."
            )

        # Guardamos el nombre ya limpio.
        datos_actualizados["nombre"] = nombre_limpio

    # Evitamos asignar una sucursal nula.
    if "sucursal_id" in datos_actualizados:
        if datos_actualizados["sucursal_id"] is None:
            raise HTTPException(
                status_code=400,
                detail="Debes indicar una sucursal válida."
            )

        # Buscamos la sucursal seleccionada.
        sucursal = db.query(Sucursal).filter(
            Sucursal.id == datos_actualizados["sucursal_id"]
        ).first()

        # Verificamos que la sucursal exista.
        if sucursal is None:
            raise HTTPException(
                status_code=404,
                detail="No se encontró la sucursal seleccionada."
            )

        # Solo impedimos asignar una sucursal inactiva
        # cuando se intenta cambiar a ella desde otra sucursal.
        # Así se pueden editar equipos que ya pertenecen
        # a sucursales que fueron desactivadas posteriormente.
        if (
            not sucursal.activo
            and sucursal.id != equipo.sucursal_id
        ):
            raise HTTPException(
                status_code=400,
                detail="No se puede asignar el equipo a una sucursal inactiva."
            )

    # Conservamos el nombre anterior para documentar el cambio.
    nombre_anterior = equipo.nombre

    # Actualizamos los campos proporcionados.
    for campo, valor in datos_actualizados.items():
        setattr(equipo, campo, valor)

    try:
        # Creamos el evento que documenta la actualización.
        nuevo_historial = Historial(
            modulo="equipos",
            accion="actualizacion",
            descripcion=(
                f"Se actualizó el equipo '{nombre_anterior}' "
                f"(ID {equipo.id}). "
                f"Nombre actual: '{equipo.nombre}'."
            ),
            entidad="equipo",
            entidad_id=equipo.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma sesión.
        db.add(nuevo_historial)

        # Guardamos los cambios del equipo y su historial juntos.
        db.commit()

        # Recuperamos los datos actualizados.
        db.refresh(equipo)

    except IntegrityError:
        # Revertimos los cambios si ocurre un error.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo actualizar el equipo. "
                "Verifica que la sucursal exista y que los datos sean válidos."
            )
        )

    # Devolvemos la información actualizada.
    return {
        "id": equipo.id,
        "sucursal_id": equipo.sucursal_id,
        "nombre": equipo.nombre,
        "tipo_equipo": equipo.tipo_equipo,
        "marca": equipo.marca,
        "modelo": equipo.modelo,
        "numero_serie": equipo.numero_serie,
        "estado": equipo.estado
    }


# ==========================================================
# ELIMINAR UN EQUIPO DE FORMA CONTROLADA
# ==========================================================

@router.delete("/{equipo_id}")
def eliminar_equipo(
    equipo_id: int,
    db: Session = Depends(get_db)
):

    # Buscamos el equipo que se desea eliminar.
    equipo = db.query(Equipo).filter(
        Equipo.id == equipo_id
    ).first()

    # Si no existe, devolvemos un error 404.
    if equipo is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el equipo solicitado."
        )

    # Contamos los mantenimientos relacionados con el equipo.
    mantenimientos_asociados = db.query(Mantenimiento).filter(
        Mantenimiento.equipo_id == equipo_id
    ).count()

    # Contamos los respaldos relacionados con el equipo.
    respaldos_asociados = db.query(Respaldo).filter(
        Respaldo.equipo_id == equipo_id
    ).count()

    # Si existen registros relacionados, bloqueamos la eliminación.
    if mantenimientos_asociados > 0 or respaldos_asociados > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar el equipo porque tiene registros relacionados. "
                f"Mantenimientos: {mantenimientos_asociados}. "
                f"Respaldos: {respaldos_asociados}. "
                "Conserva su historial o desactiva el equipo."
            )
        )

    # Conservamos el nombre antes de eliminar el registro.
    nombre_equipo = equipo.nombre

    try:
        # Creamos primero el evento para conservar la información.
        nuevo_historial = Historial(
            modulo="equipos",
            accion="eliminacion",
            descripcion=(
                f"Se eliminó el equipo '{nombre_equipo}' "
                f"(ID {equipo_id})."
            ),
            entidad="equipo",
            entidad_id=equipo_id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma sesión.
        db.add(nuevo_historial)

        # Marcamos el equipo para eliminarlo.
        db.delete(equipo)

        # Confirmamos la eliminación y el historial juntos.
        db.commit()

    except IntegrityError:
        # Revertimos los cambios si existe otra restricción.
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar el equipo porque existen "
                "otros registros relacionados."
            )
        )

    # Confirmamos que la eliminación se realizó correctamente.
    return {
        "mensaje": "Equipo eliminado correctamente.",
        "id": equipo_id
    }
