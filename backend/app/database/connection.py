import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Carga las variables de configuración que se encuentran en el archivo .env
load_dotenv()

# Obtiene los datos de conexión desde las variables de entorno
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Construye la URL que SQLAlchemy utilizará para conectarse a PostgreSQL
DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Crea el motor de conexión a la base de datos
# El engine será utilizado por SQLAlchemy para comunicarse con PostgreSQL
engine = create_engine(DATABASE_URL)