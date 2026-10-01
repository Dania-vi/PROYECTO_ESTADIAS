from collections.abc import Generator

from app.database.session import SessionLocal


# Crea una sesión de base de datos para utilizarla dentro
# de los endpoints de FastAPI.
def get_db() -> Generator:

    # Crea una nueva sesión.
    db = SessionLocal()

    try:
        # Entrega la sesión al endpoint que la solicite.
        yield db

    finally:
        # Cierra la sesión cuando termina la operación.
        # Esto evita dejar conexiones abiertas innecesariamente.
        db.close()