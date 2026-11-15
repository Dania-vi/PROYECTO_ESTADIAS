
# Importamos FastAPI y Depends para crear la aplicación y manejar dependencias.
from fastapi import FastAPI, Depends

# Importamos el middleware para permitir la comunicación entre diferentes orígenes.
from fastapi.middleware.cors import CORSMiddleware

# Importamos herramientas para realizar consultas a PostgreSQL.
from sqlalchemy import text
from sqlalchemy.orm import Session

# Importamos la dependencia para obtener la conexión a la base de datos.
from app.database.dependencies import get_db

# Importamos las rutas del módulo de sucursales.
from app.api.sucursales import router as sucursales_router

# Importamos las rutas del módulo de equipos.
from app.api.equipos import router as equipos_router

# Importamos las rutas para consultar y registrar técnicos.
from app.api.tecnicos import router as tecnicos_router

# Importamos las rutas para consultar y registrar servidores.
from app.api.servidores import router as servidores_router

# Importamos las rutas para registrar y consultar métricas de los servidores.
from app.api.metricas_servidor import router as metricas_servidor_router

# Importamos las rutas para registrar y consultar respaldos.
from app.api.respaldos import router as respaldos_router

# Importamos las rutas para registrar y consultar alertas.
from app.api.alertas import router as alertas_router

# Importamos las rutas para consultar y registrar mantenimientos.
from app.api.mantenimientos import router as mantenimientos_router

# Importamos las rutas para consultar y registrar eventos del historial.
from app.api.historial import router as historial_router


# Creación de la aplicación principal de FastAPI.
# Desde aquí se conectan las diferentes partes del backend.
app = FastAPI(
    title="Bitacora de soporte y dashboard de monitoreo",
    description="Sistema de soporte tecnico y monitoreo para Dulceria Atilano",
    version="1.0.0"
)


# Configuramos los orígenes que tienen permiso para comunicarse con el backend.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]


# Registramos el middleware CORS en la aplicación.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registra las rutas relacionadas con las sucursales.
app.include_router(sucursales_router)

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

# Habilita las rutas del módulo de historial.
app.include_router(historial_router)


# Esta ruta sirve como prueba para comprobar que el servidor
# está funcionando correctamente.
@app.get("/api/health")
def health_check():

    # Esta ruta devuelve una respuesta indicando que
    # el sistema está funcionando.
    return {
        "status": "ok",
        "message": "El sistema esta funcionando correctamente"
    }


# Ruta de prueba para comprobar la conexión entre
# FastAPI, SQLAlchemy y PostgreSQL.
@app.get("/api/db-test")
def database_test(db: Session = Depends(get_db)):

    # Ejecutamos una consulta sencilla en PostgreSQL.
    # No modifica ningún dato de la base de datos.
    result = db.execute(text("SELECT 1"))

    # Obtenemos el resultado de la consulta.
    value = result.scalar()

    return {
        "status": "ok",
        "database": "bitacora_soporte",
        "result": value
    }
