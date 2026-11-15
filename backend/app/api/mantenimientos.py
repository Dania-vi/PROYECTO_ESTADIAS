
# Importamos las herramientas necesarias de FastAPI.
from fastapi import APIRouter, Depends, HTTPException

# Importamos la sesión de SQLAlchemy y el error de integridad.
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importamos la dependencia para conectarnos a PostgreSQL.
from app.database.dependencies import get_db

# Importamos los modelos necesarios.
from app.models.mantenimiento import Mantenimiento
from app.models.equipo import Equipo
from app.models.tecnico import Tecnico
from app.models.historial import Historial

# Importamos los esquemas de validación.
from app.schemas.mantenimiento import MantenimientoCreate, MantenimientoUpdate


# Creamos el router para administrar los mantenimientos.
router = APIRouter(
    prefix="/api/mantenimientos",
    tags=["Mantenimientos"]
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

    # No permitimos asignar equipos que estén inactivos.
    if equipo.estado == "Inactivo":
        raise HTTPException(
            status_code=400,
            detail="No se pueden asignar equipos inactivos a nuevos mantenimientos."
        )

    return equipo


# ==========================================================
# VALIDAR TÉCNICO
# ==========================================================

def validar_tecnico(tecnico_id: int, db: Session):
    # Buscamos el técnico por su identificador.
    tecnico = db.query(Tecnico).filter(
        Tecnico.id == tecnico_id
    ).first()

    # Comprobamos que el técnico exista.
    if tecnico is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el técnico seleccionado."
        )

    # Solo permitimos asignar técnicos activos.
    if not tecnico.activo:
        raise HTTPException(
            status_code=400,
            detail="No se pueden asignar técnicos inactivos a nuevos mantenimientos."
        )

    return tecnico


# ==========================================================
# CONSULTAR TODOS LOS MANTENIMIENTOS
# ==========================================================

@router.get("/")
def obtener_mantenimientos(db: Session = Depends(get_db)):

    # Consultamos todos los registros de mantenimiento.
    mantenimientos = db.query(Mantenimiento).all()

    # Convertimos los registros a una lista de objetos JSON.
    return [
        {
            "id": mantenimiento.id,
            "equipo_id": mantenimiento.equipo_id,
            "tecnico_id": mantenimiento.tecnico_id,
            "fecha_mantenimiento": mantenimiento.fecha_mantenimiento,
            "tipo_mantenimiento": mantenimiento.tipo_mantenimiento,
            "problema_detectado": mantenimiento.problema_detectado,
            "solucion_aplicada": mantenimiento.solucion_aplicada,
            "tiempo_empleado_min": mantenimiento.tiempo_empleado_min,
            "observaciones": mantenimiento.observaciones,
        }
        for mantenimiento in mantenimientos
    ]


# ==========================================================
# REGISTRAR UN NUEVO MANTENIMIENTO
# ==========================================================

@router.post("/")
def crear_mantenimiento(
    datos: MantenimientoCreate,
    db: Session = Depends(get_db)
):

    # Validamos que el equipo exista y no esté inactivo.
    validar_equipo(datos.equipo_id, db)

    # Validamos que el técnico exista y esté activo.
    validar_tecnico(datos.tecnico_id, db)

    # Construimos el registro con los datos recibidos.
    nuevo_mantenimiento = Mantenimiento(
        equipo_id=datos.equipo_id,
        tecnico_id=datos.tecnico_id,
        tipo_mantenimiento=datos.tipo_mantenimiento,
        problema_detectado=datos.problema_detectado,
        solucion_aplicada=datos.solucion_aplicada,
        tiempo_empleado_min=datos.tiempo_empleado_min,
        observaciones=datos.observaciones,
    )

    try:
        # Agregamos el mantenimiento a la sesión.
        db.add(nuevo_mantenimiento)

        # Enviamos el INSERT para obtener el ID generado.
        # Todavía no confirmamos la transacción.
        db.flush()

        # Creamos el evento que documenta el registro.
        nuevo_historial = Historial(
            modulo="mantenimientos",
            accion="creacion",
            descripcion=(
                f"Se registró un mantenimiento "
                f"{nuevo_mantenimiento.tipo_mantenimiento} "
                f"para el equipo ID {nuevo_mantenimiento.equipo_id}."
            ),
            entidad="mantenimiento",
            entidad_id=nuevo_mantenimiento.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma transacción.
        db.add(nuevo_historial)

        # Confirmamos ambas operaciones juntas.
        db.commit()

        # Recuperamos los datos guardados.
        db.refresh(nuevo_mantenimiento)

    except IntegrityError:
        # Revertimos ambas operaciones si ocurre un error.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar el mantenimiento. "
                "Verifica que los datos sean válidos."
            )
        )

    # Devolvemos los datos del mantenimiento registrado.
    return {
        "id": nuevo_mantenimiento.id,
        "equipo_id": nuevo_mantenimiento.equipo_id,
        "tecnico_id": nuevo_mantenimiento.tecnico_id,
        "fecha_mantenimiento": nuevo_mantenimiento.fecha_mantenimiento,
        "tipo_mantenimiento": nuevo_mantenimiento.tipo_mantenimiento,
        "problema_detectado": nuevo_mantenimiento.problema_detectado,
        "solucion_aplicada": nuevo_mantenimiento.solucion_aplicada,
        "tiempo_empleado_min": nuevo_mantenimiento.tiempo_empleado_min,
        "observaciones": nuevo_mantenimiento.observaciones,
    }


# ==========================================================
# ACTUALIZAR UN MANTENIMIENTO EXISTENTE
# ==========================================================

@router.put("/{mantenimiento_id}")
def actualizar_mantenimiento(
    mantenimiento_id: int,
    datos: MantenimientoUpdate,
    db: Session = Depends(get_db)
):

    # Buscamos el mantenimiento mediante su identificador.
    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    # Comprobamos que el mantenimiento exista.
    if mantenimiento is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el mantenimiento solicitado."
        )

    # Obtenemos únicamente los campos enviados por el frontend.
    datos_actualizados = datos.model_dump(exclude_unset=True)

    # Evitamos realizar actualizaciones vacías.
    if not datos_actualizados:
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un campo para actualizar."
        )

    # No permitimos eliminar las asignaciones obligatorias.
    if "equipo_id" in datos_actualizados:
        if datos_actualizados["equipo_id"] is None:
            raise HTTPException(
                status_code=400,
                detail="El equipo asignado no puede estar vacío."
            )

    if "tecnico_id" in datos_actualizados:
        if datos_actualizados["tecnico_id"] is None:
            raise HTTPException(
                status_code=400,
                detail="El técnico asignado no puede estar vacío."
            )

    # No permitimos dejar el tipo de mantenimiento vacío.
    if (
        "tipo_mantenimiento" in datos_actualizados
        and datos_actualizados["tipo_mantenimiento"] is None
    ):
        raise HTTPException(
            status_code=400,
            detail="El tipo de mantenimiento no puede estar vacío."
        )

    # Comprobamos si realmente se está cambiando el equipo.
    if (
        "equipo_id" in datos_actualizados
        and datos_actualizados["equipo_id"] != mantenimiento.equipo_id
    ):
        # Validamos el nuevo equipo únicamente cuando cambia la asignación.
        validar_equipo(datos_actualizados["equipo_id"], db)

    # Comprobamos si realmente se está cambiando el técnico.
    if (
        "tecnico_id" in datos_actualizados
        and datos_actualizados["tecnico_id"] != mantenimiento.tecnico_id
    ):
        # Validamos el nuevo técnico únicamente cuando cambia la asignación.
        validar_tecnico(datos_actualizados["tecnico_id"], db)

    # Guardamos la información anterior para documentar el historial.
    equipo_anterior = mantenimiento.equipo_id
    tecnico_anterior = mantenimiento.tecnico_id

    # Actualizamos únicamente los campos que fueron enviados.
    for campo, valor in datos_actualizados.items():
        setattr(mantenimiento, campo, valor)

    try:
        # Creamos el evento que documenta la actualización.
        nuevo_historial = Historial(
            modulo="mantenimientos",
            accion="actualizacion",
            descripcion=(
                f"Se actualizó el mantenimiento ID {mantenimiento.id}. "
                f"Equipo anterior: {equipo_anterior}; "
                f"equipo actual: {mantenimiento.equipo_id}. "
                f"Técnico anterior: {tecnico_anterior}; "
                f"técnico actual: {mantenimiento.tecnico_id}."
            ),
            entidad="mantenimiento",
            entidad_id=mantenimiento.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma transacción.
        db.add(nuevo_historial)

        # Confirmamos juntos los cambios y el historial.
        db.commit()

        # Recuperamos el registro actualizado.
        db.refresh(mantenimiento)

    except IntegrityError:
        # Revertimos los cambios si ocurre un error.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo actualizar el mantenimiento. "
                "Verifica que los datos sean válidos."
            )
        )

    # Devolvemos el mantenimiento actualizado.
    return {
        "id": mantenimiento.id,
        "equipo_id": mantenimiento.equipo_id,
        "tecnico_id": mantenimiento.tecnico_id,
        "fecha_mantenimiento": mantenimiento.fecha_mantenimiento,
        "tipo_mantenimiento": mantenimiento.tipo_mantenimiento,
        "problema_detectado": mantenimiento.problema_detectado,
        "solucion_aplicada": mantenimiento.solucion_aplicada,
        "tiempo_empleado_min": mantenimiento.tiempo_empleado_min,
        "observaciones": mantenimiento.observaciones,
    }


# ==========================================================
# ELIMINAR UN MANTENIMIENTO EXISTENTE
# ==========================================================

@router.delete("/{mantenimiento_id}")
def eliminar_mantenimiento(
    mantenimiento_id: int,
    db: Session = Depends(get_db)
):

    # Buscamos el mantenimiento que se desea eliminar.
    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    # Comprobamos que el mantenimiento exista.
    if mantenimiento is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el mantenimiento que deseas eliminar."
        )

    try:
        # Creamos primero el evento para conservar los datos del registro.
        nuevo_historial = Historial(
            modulo="mantenimientos",
            accion="eliminacion",
            descripcion=(
                f"Se eliminó el mantenimiento ID {mantenimiento.id} "
                f"del equipo ID {mantenimiento.equipo_id}."
            ),
            entidad="mantenimiento",
            entidad_id=mantenimiento.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la sesión.
        db.add(nuevo_historial)

        # Marcamos el mantenimiento para eliminarlo.
        db.delete(mantenimiento)

        # Confirmamos la eliminación y el historial juntos.
        db.commit()

    except IntegrityError:
        # Revertimos las operaciones si existe una restricción.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo eliminar el mantenimiento porque "
                "existen restricciones relacionadas con este registro."
            )
        )

    # Devolvemos la confirmación de eliminación.
    return {
        "mensaje": "El mantenimiento se eliminó correctamente.",
        "id": mantenimiento_id
    }
