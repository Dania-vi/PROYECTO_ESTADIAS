from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.sucursal import Sucursal
from app.schemas.sucursal import SucursalCreate


# Router para agrupar los endpoints relacionados
# con las sucursales.
router = APIRouter(
    prefix="/api/sucursales",
    tags=["Sucursales"]
)


# Endpoint para consultar todas las sucursales registradas.
@router.get("/")
def obtener_sucursales(db: Session = Depends(get_db)):

    # Consulta todos los registros de la tabla sucursales.
    sucursales = db.query(Sucursal).all()

    # Convierte los registros de SQLAlchemy en datos
    # que FastAPI puede devolver como respuesta JSON.
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


# Endpoint para registrar una nueva sucursal.
@router.post("/")
def crear_sucursal(
    sucursal_data: SucursalCreate,
    db: Session = Depends(get_db)
):

    # Crea un objeto Sucursal utilizando los datos
    # recibidos y validados por Pydantic.
    nueva_sucursal = Sucursal(
        nombre=sucursal_data.nombre,
        direccion=sucursal_data.direccion,
        telefono=sucursal_data.telefono,
        activo=sucursal_data.activo
    )

    # Agrega la nueva sucursal a la sesión.
    db.add(nueva_sucursal)

    # Confirma la operación para guardar el registro
    # permanentemente en PostgreSQL.
    db.commit()

    # Actualiza el objeto con el ID generado automáticamente
    # por PostgreSQL.
    db.refresh(nueva_sucursal)

    # Devuelve los datos de la sucursal recién creada.
    return {
        "id": nueva_sucursal.id,
        "nombre": nueva_sucursal.nombre,
        "direccion": nueva_sucursal.direccion,
        "telefono": nueva_sucursal.telefono,
        "activo": nueva_sucursal.activo
    }