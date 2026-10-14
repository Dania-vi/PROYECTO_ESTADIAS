from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.api.sucursales import router as sucursales_router
from app.api.equipos import router as equipos_router

# Importa las rutas para consultar y registrar técnicos.
from app.api.tecnicos import router as tecnicos_router

# Importa las rutas para consultar y registrar servidores.
from app.api.servidores import router as servidores_router


# Importa las rutas para registrar y consultar métricas de los servidores.
from app.api.metricas_servidor import router as metricas_servidor_router


# Importa las rutas para registrar y consultar respaldos.
from app.api.respaldos import router as respaldos_router


# Importa las rutas para registrar y consultar alertas.
from app.api.alertas import router as alertas_router


# Importa las rutas para consultar y registrar mantenimientos.
from app.api.mantenimientos import router as mantenimientos_router


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

# Habilita las rutas del módulo de técnicos.
app.include_router(tecnicos_router)

# Habilita las rutas del módulo de servidores.
app.include_router(servidores_router)


# Habilita las rutas del módulo de métricas de servidores.
app.include_router(metricas_servidor_router)


# Habilita las rutas del módulo de respaldos.
app.include_router(respaldos_router)


# Habilita las rutas del módulo de alertas.
app.include_router(alertas_router)


# Habilita las rutas del módulo de mantenimientos.
app.include_router(mantenimientos_router)




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