from sqlalchemy.orm import sessionmaker

from app.database.connection import engine


# Crea una fábrica de sesiones para comunicarnos con PostgreSQL.
# Cada vez que necesitemos trabajar con la base de datos,
# podremos crear una nueva sesión a partir de esta configuración.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)