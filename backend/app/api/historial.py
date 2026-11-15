
# Importamos las herramientas necesarias de FastAPI.
from fastapi import APIRouter, Depends, HTTPException

# Importamos la sesión de SQLAlchemy.
from sqlalchemy.orm import Session

# Importamos la dependencia para obtener la conexión a la base de datos.
from app.database.dependencies import get_db

# Importamos el modelo de historial.
from app.models.historial import Historial

# Importamos los esquemas de historial.
from app.schemas.historial import HistorialCreate, HistorialResponse


# Definimos las rutas relacionadas con el historial.
router = APIRouter(
    prefix="/api/historial",
    tags=["Historial"]
)


# CONSULTAR TODOS LOS EVENTOS DEL HISTORIAL.
@router.get("/", response_model=list[HistorialResponse])
def obtener_historial(db: Session = Depends(get_db)):

    # Consultamos todos los eventos ordenados del más reciente al más antiguo.
    historial = db.query(Historial).order_by(
        Historial.fecha_hora.desc()
    ).all()

    # Devolvemos los registros encontrados.
    return historial


# CONSULTAR UN EVENTO DEL HISTORIAL POR SU ID.
@router.get("/{historial_id}", response_model=HistorialResponse)
def obtener_evento(
    historial_id: int,
    db: Session = Depends(get_db)
):

    # Buscamos el evento mediante su identificador.
    evento = db.query(Historial).filter(
        Historial.id == historial_id
    ).first()

    # Comprobamos si el evento existe.
    if evento is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el evento solicitado."
        )

    # Devolvemos el evento encontrado.
    return evento


# REGISTRAR UN NUEVO EVENTO EN EL HISTORIAL.
@router.post("/", response_model=HistorialResponse, status_code=201)
def crear_evento(
    datos: HistorialCreate,
    db: Session = Depends(get_db)
):

    # Construimos el nuevo registro con los datos recibidos.
    nuevo_evento = Historial(
        modulo=datos.modulo,
        accion=datos.accion,
        descripcion=datos.descripcion,
        entidad=datos.entidad,
        entidad_id=datos.entidad_id,
        usuario=datos.usuario
    )

    # Agregamos el evento a la sesión de SQLAlchemy.
    db.add(nuevo_evento)

    try:
        # Guardamos el evento en PostgreSQL.
        db.commit()

        # Recuperamos los datos generados por la base de datos.
        db.refresh(nuevo_evento)

    except Exception:
        # Revertimos la operación si ocurre algún error.
        db.rollback()

        # Devolvemos un mensaje de error controlado.
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar el evento en el historial."
        )

    # Devolvemos el evento registrado.
    return nuevo_evento
