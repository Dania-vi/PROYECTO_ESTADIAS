from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.api.sucursales import router as sucursales_router
from app.api.equipos import router as equipos_router


# Creacion de la aplicacion principal de FastAPI
# Desde aqui se comienzan a conectar las diferentes partes del backend

app = FastAPI(
    title="Bitacora de soporte y dashboard de monitoreo",
    description="Sistema de soporte tecnico y monitoreo para Dulceria Atilano",
    version="1.0.0"
)


# Registra las rutas relacionadas con las sucursales.
app.include_router(sucursales_router)
# Registra las rutas relacionadas con los equipos.

# Registra las rutas relacionadas con los equipos.
app.include_router(equipos_router)


# Esta ruta sirve como prueba para comprobar que el servidor
# esta funcionando correctamente.
@app.get("/api/health")
def health_check():

    # Esta ruta devuelve una respuesta indicando que
    # el sistema esta funcionando.
    return {
        "status": "ok",
        "message": "El sistema esta funcionando correctamente"
    }


# Ruta de prueba para comprobar la conexion entre
# FastAPI, SQLAlchemy y PostgreSQL.
@app.get("/api/db-test")
def database_test(db: Session = Depends(get_db)):

    # Ejecutamos una consulta sencilla en PostgreSQL.
    # No modifica ningun dato de la base de datos.
    result = db.execute(text("SELECT 1"))

    # Obtenemos el resultado de la consulta.
    value = result.scalar()

    return {
        "status": "ok",
        "database": "bitacora_soporte",
        "result": value
    }