
# Importamos las herramientas necesarias de FastAPI.
from fastapi import APIRouter, Depends, HTTPException

# Importamos la sesión de SQLAlchemy.
from sqlalchemy.orm import Session

# Importamos la excepción para manejar errores de integridad.
from sqlalchemy.exc import IntegrityError

# Importamos la dependencia para obtener la conexión a la base de datos.
from app.database.dependencies import get_db

# Importamos los modelos de sucursales, equipos e historial.
from app.models.sucursal import Sucursal
from app.models.equipo import Equipo
from app.models.historial import Historial

# Importamos los esquemas para crear y actualizar sucursales.
from app.schemas.sucursal import SucursalCreate, SucursalUpdate


# Creamos el router para administrar las sucursales.
router = APIRouter(
    prefix="/api/sucursales",
    tags=["Sucursales"]
)


# ==========================================================
# CONSULTAR SUCURSALES
# ==========================================================

@router.get("/")
def obtener_sucursales(db: Session = Depends(get_db)):

    # Consultamos todas las sucursales registradas.
    sucursales = db.query(Sucursal).all()

    # Devolvemos los datos de cada sucursal.
    return [
        {
            "id": sucursal.id,
            "nombre": sucursal.nombre,
            "direccion": sucursal.direccion,
            "telefono": sucursal.telefono,
            "activo": sucursal.activo
        }
        for sucursal in sucursales
    ]


# ==========================================================
# REGISTRAR UNA NUEVA SUCURSAL
# ==========================================================

@router.post("/")
def crear_sucursal(
    sucursal_data: SucursalCreate,
    db: Session = Depends(get_db)
):

    # Creamos una nueva instancia del modelo Sucursal.
    nueva_sucursal = Sucursal(
        nombre=sucursal_data.nombre,
        direccion=sucursal_data.direccion,
        telefono=sucursal_data.telefono,
        activo=sucursal_data.activo
    )

    try:
        # Agregamos la sucursal a la sesión.
        db.add(nueva_sucursal)

        # Ejecutamos el INSERT sin confirmar la transacción.
        # Así obtenemos el ID generado para la sucursal.
        db.flush()

        # Creamos el evento que documenta el registro.
        nuevo_historial = Historial(
            modulo="sucursales",
            accion="creacion",
            descripcion=(
                f"Se registró la sucursal "
                f"'{nueva_sucursal.nombre}'."
            ),
            entidad="sucursal",
            entidad_id=nueva_sucursal.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma sesión.
        db.add(nuevo_historial)

        # Confirmamos la sucursal y su historial juntos.
        db.commit()

        # Recuperamos los datos guardados.
        db.refresh(nueva_sucursal)

    except IntegrityError:
        # Revertimos ambas operaciones si ocurre un error.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo registrar la sucursal. "
                "Verifica que los datos sean válidos."
            )
        )

    # Devolvemos la sucursal registrada.
    return {
        "id": nueva_sucursal.id,
        "nombre": nueva_sucursal.nombre,
        "direccion": nueva_sucursal.direccion,
        "telefono": nueva_sucursal.telefono,
        "activo": nueva_sucursal.activo
    }


# ==========================================================
# ACTUALIZAR UNA SUCURSAL
# ==========================================================

@router.put("/{sucursal_id}")
def actualizar_sucursal(
    sucursal_id: int,
    datos: SucursalUpdate,
    db: Session = Depends(get_db)
):

    # Buscamos la sucursal mediante su identificador.
    sucursal = db.query(Sucursal).filter(
        Sucursal.id == sucursal_id
    ).first()

    # Verificamos que la sucursal exista.
    if sucursal is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la sucursal solicitada."
        )

    # Obtenemos únicamente los campos enviados.
    datos_actualizados = datos.model_dump(exclude_unset=True)

    # Evitamos procesar una actualización vacía.
    if not datos_actualizados:
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un campo para actualizar."
        )

    # Evitamos asignar un nombre nulo.
    if "nombre" in datos_actualizados and datos_actualizados["nombre"] is None:
        raise HTTPException(
            status_code=400,
            detail="El nombre de la sucursal no puede estar vacío."
        )

    # Guardamos el nombre anterior para documentar el cambio.
    nombre_anterior = sucursal.nombre

    # Actualizamos los campos proporcionados.
    for campo, valor in datos_actualizados.items():
        setattr(sucursal, campo, valor)

    try:
        # Creamos el evento que documenta la actualización.
        nuevo_historial = Historial(
            modulo="sucursales",
            accion="actualizacion",
            descripcion=(
                f"Se actualizó la sucursal '{nombre_anterior}'. "
                f"Nombre actual: '{sucursal.nombre}'."
            ),
            entidad="sucursal",
            entidad_id=sucursal.id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma sesión.
        db.add(nuevo_historial)

        # Guardamos la actualización y el historial juntos.
        db.commit()

        # Recuperamos los datos actualizados.
        db.refresh(sucursal)

    except IntegrityError:
        # Revertimos ambas operaciones si ocurre un error.
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="No se pudo actualizar la sucursal."
        )

    # Devolvemos la información actualizada.
    return {
        "id": sucursal.id,
        "nombre": sucursal.nombre,
        "direccion": sucursal.direccion,
        "telefono": sucursal.telefono,
        "activo": sucursal.activo
    }


# ==========================================================
# ELIMINAR UNA SUCURSAL DE FORMA CONTROLADA
# ==========================================================

@router.delete("/{sucursal_id}")
def eliminar_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db)
):

    # Buscamos la sucursal que se desea eliminar.
    sucursal = db.query(Sucursal).filter(
        Sucursal.id == sucursal_id
    ).first()

    # Si no existe, devolvemos un error 404.
    if sucursal is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la sucursal solicitada."
        )

    # Contamos los equipos asociados a esta sucursal.
    equipos_asociados = db.query(Equipo).filter(
        Equipo.sucursal_id == sucursal_id
    ).count()

    # Si existen equipos asociados, bloqueamos la eliminación.
    if equipos_asociados > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No se puede eliminar la sucursal porque tiene "
                f"{equipos_asociados} equipo(s) asociado(s). "
                "Primero debes reasignar o retirar esos equipos."
            )
        )

    # Conservamos el nombre antes de eliminar el registro.
    nombre_sucursal = sucursal.nombre

    try:
        # Creamos primero el evento para conservar la información.
        nuevo_historial = Historial(
            modulo="sucursales",
            accion="eliminacion",
            descripcion=(
                f"Se eliminó la sucursal '{nombre_sucursal}' "
                f"(ID {sucursal_id})."
            ),
            entidad="sucursal",
            entidad_id=sucursal_id,
            usuario="Administrador"
        )

        # Agregamos el evento a la misma sesión.
        db.add(nuevo_historial)

        # Marcamos la sucursal para eliminarla.
        db.delete(sucursal)

        # Confirmamos la eliminación y el historial juntos.
        db.commit()

    except IntegrityError:
        # Revertimos ambas operaciones si existe una restricción.
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar la sucursal "
                "porque tiene registros relacionados."
            )
        )

    # Devolvemos la confirmación de eliminación.
    return {
        "mensaje": "Sucursal eliminada correctamente.",
        "id": sucursal_id
    }
