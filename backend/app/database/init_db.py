from app.database.base import Base
from app.database.connection import engine

# Importamos los ocho modelos de la base de datos.
# Esto permite que SQLAlchemy conozca todas las tablas
# antes de ejecutar la creación de la base de datos.
from app.models.sucursal import Sucursal
from app.models.equipo import Equipo
from app.models.tecnico import Tecnico
from app.models.mantenimiento import Mantenimiento
from app.models.servidor import Servidor
from app.models.metrica_servidor import MetricaServidor
from app.models.respaldo import Respaldo
from app.models.alerta import Alerta


# Función encargada de crear las tablas de la base de datos.
def init_db():

    # SQLAlchemy revisa los modelos registrados en Base.metadata
    # y crea las tablas que todavía no existen en PostgreSQL.
    Base.metadata.create_all(bind=engine)

    print("Tablas creadas correctamente")


# Ejecuta la función cuando este archivo se ejecuta directamente.
if __name__ == "__main__":
    init_db()