import smtplib
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FIRMA_NOMBRE = os.getenv("FIRMA_NOMBRE")
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
CALENDLY_URL = os.getenv("CALENDLY_URL")


def enviar_correos(
    correos_df,
    html_template_str,
    enviados_existentes=set(),
    max_envios=1000,
    callback=None,
):

    resultados = []
    enviados_actuales = set(enviados_existentes)
    count = 0
    total = min(len(correos_df), max_envios)

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    firma_nombre = os.getenv("FIRMA_NOMBRE")
    whatsapp_url = os.getenv("WHATSAPP_URL")
    calendly_url = os.getenv("CALENDLY_URL")

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)

        for _, row in correos_df.iterrows():
            nombre = row["nombre"]
            email = row["email"]
            if email in enviados_actuales:
                continue

            html_content = (
                html_template_str.replace("{nombre}", nombre)
                .replace("{whatsapp_url}", whatsapp_url)
                .replace("{calendly_url}", calendly_url)
                .replace("{firma_nombre}", firma_nombre)
                .replace("{año_actual}", str(datetime.now().year))
            )

            msg = EmailMessage()
            msg["Subject"] = "¿Podemos ayudarte a potenciar tu negocio digital?"
            msg["From"] = f"PrometeonDev - Desarrollo Digital <{smtp_user}>"
            msg["To"] = email
            msg.set_content("Este mensaje requiere un cliente compatible con HTML.")
            msg.add_alternative(html_content, subtype="html")

            try:
                smtp.send_message(msg)
                enviados_actuales.add(email)
                count += 1
                mensaje = f"✅ Enviado a: {email}"
                print(mensaje)
                resultados.append(mensaje)

                os.makedirs("csv", exist_ok=True)
                with open("csv/enviados.csv", "a", encoding="utf-8") as f:
                    if count == 1 and not os.path.exists("csv/enviados.csv"):
                        f.write("email\n")
                    f.write(email + "\n")

            except Exception as e:
                mensaje = f"❌ Error al enviar a {email}: {e}"
                resultados.append(mensaje)

            # Callback para la interfaz Streamlit
            if callback:
                callback(count, total, mensaje)

            if count >= max_envios:
                break

    return resultados
