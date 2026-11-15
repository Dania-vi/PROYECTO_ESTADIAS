
# Permite crear y enviar mensajes de correo electrónico.
import smtplib

# Permite construir mensajes con asunto, remitente y destinatarios.
from email.message import EmailMessage

# Permite leer la configuración del archivo .env.
import os
from dotenv import load_dotenv

# Permite registrar errores sin detener el monitoreo.
import logging


# Configura el registro de errores del servicio.
logger = logging.getLogger(__name__)

# Carga las variables de entorno del proyecto.
load_dotenv()


def enviar_correo_alerta(asunto: str, mensaje: str) -> bool:
    """
    Envía un correo electrónico con la información de una alerta.

    Obtiene los datos SMTP y los destinatarios desde el archivo .env.

    Devuelve:
    - True si el correo se envió correctamente.
    - False si falta configuración o ocurre un error.
    """

    # Obtiene los datos de conexión SMTP.
    servidor_smtp = os.getenv("SMTP_HOST", "smtp.gmail.com")
    puerto_smtp = int(os.getenv("SMTP_PORT", "587"))
    correo_remitente = os.getenv("SMTP_USER", "").strip()
    contrasena = os.getenv("SMTP_PASSWORD", "").strip()

    # Obtiene los destinatarios y elimina espacios innecesarios.
    destinatarios = [
        correo.strip()
        for correo in os.getenv("ALERT_RECIPIENTS", "").split(",")
        if correo.strip()
    ]

    # Comprueba que exista toda la configuración necesaria.
    if not correo_remitente or not contrasena or not destinatarios:
        logger.warning(
            "No se envió el correo: falta configurar SMTP_USER, "
            "SMTP_PASSWORD o ALERT_RECIPIENTS."
        )
        return False

    # Construye el mensaje de correo.
    correo = EmailMessage()
    correo["Subject"] = asunto
    correo["From"] = correo_remitente
    correo["To"] = ", ".join(destinatarios)
    correo.set_content(mensaje)

    try:
        # Establece la conexión con el servidor SMTP.
        with smtplib.SMTP(
            servidor_smtp,
            puerto_smtp,
            timeout=20
        ) as servidor:

            # Identifica el cliente ante el servidor de correo.
            servidor.ehlo()

            # Activa la conexión cifrada.
            servidor.starttls()

            # Vuelve a identificarse después de activar TLS.
            servidor.ehlo()

            # Inicia sesión con las credenciales configuradas.
            servidor.login(correo_remitente, contrasena)

            # Envía el mensaje a todos los destinatarios.
            servidor.send_message(correo)

        # Informa que el envío terminó correctamente.
        logger.info("Correo de alerta enviado correctamente.")
        return True

    except Exception:
        # Registra el error sin mostrar contraseñas ni detener el sistema.
        logger.exception("No fue posible enviar el correo de alerta.")
        return False
