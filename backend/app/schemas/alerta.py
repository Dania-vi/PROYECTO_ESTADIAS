from pydantic import BaseModel, Field


# Esquema para recibir los datos de una alerta nueva.
class AlertaCreate(BaseModel):
    # Los identificadores son opcionales, pero si se envían deben ser positivos.
    servidor_id: int | None = Field(default=None, gt=0)
    respaldo_id: int | None = Field(default=None, gt=0)

    # El tipo de alerta es obligatorio y debe caber en la columna de la base de datos.
    tipo_alerta: str = Field(min_length=1, max_length=30)

    # Datos complementarios de la alerta.
    metrica_afectada: str | None = Field(default=None, max_length=30)
    valor_registrado: str | None = Field(default=None, max_length=50)
    nivel_alerta: str | None = Field(default=None, max_length=20)
    mensaje: str | None = None

    # Por defecto, la alerta todavía no ha enviado correo.
    correo_enviado: bool = False
