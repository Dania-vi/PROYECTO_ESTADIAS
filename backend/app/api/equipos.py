from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.equipo import Equipo


# Router para agrupar los endpoints relacionados
# con los equipos.
router = APIRouter(
    prefix="/api/equipos",
    tags=["Equipos"]
)


# Endpoint para consultar todos los equipos registrados.
@router.get("/")
def obtener_equipos(db: Session = Depends(get_db)):

    # Consulta todos los registros de la tabla equipos.
    equipos = db.query(Equipo).all()

    # Convierte los registros de SQLAlchemy en datos
    # que FastAPI puede devolver como respuesta JSON.
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