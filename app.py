import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from correo_utils import enviar_correos as enviar_func
from verificar_utils import verificar_correos

load_dotenv()

st.set_page_config(page_title="PrometeonMailer", page_icon="📧", layout="centered")

# Acceso restringido
st.sidebar.markdown("🔐 Acceso restringido")
clave_ingresada = st.sidebar.text_input("Contraseña de acceso", type="password")
CLAVE_SECRETA = os.getenv("SECRET_KEY")
acceso_autorizado = clave_ingresada == CLAVE_SECRETA

st.title("Prometeon - Envío de Correos Masivos")

tabs = st.tabs(["📨 Enviar correos", "📋 Verificar correos"])

with tabs[0]:
    # Cargar plantilla
    with open("plantilla_prometeon_email.html", encoding="utf-8") as f:
        plantilla = f.read()

    # Subir CSV
    archivo_csv = st.file_uploader("Sube el archivo CSV de correos", type=["csv"])

    if archivo_csv:
        df = pd.read_csv(archivo_csv)
        st.dataframe(df)

        # Subida de CSVs opcionales
        col1, col2 = st.columns(2)
        enviados_csv = col1.file_uploader(
            "📂 Lista de correos ya enviados (opcional)", type=["csv"], key="enviados"
        )
        baja_csv = col2.file_uploader(
            "📂 Lista de correos dados de baja (opcional)", type=["csv"], key="baja"
        )

        max_envios = st.number_input(
            "🔢 ¿Cuántos correos deseas enviar?",
            min_value=1,
            max_value=1000,
            value=50,
            step=1,
            help="Límite diario recomendado: 50",
        )

        if st.button("📨 Enviar correos"):
            if not acceso_autorizado:
                st.error(
                    "🚫 No tienes permiso para enviar correos. Ingresa la clave correcta en el panel lateral."
                )
                st.stop()

            progreso = st.progress(0)
            resultados_box = st.empty()
            resultados = []

            # Leer enviados existentes si se subió
            enviados_existentes = set()
            if enviados_csv:
                enviados_df = pd.read_csv(enviados_csv)
                enviados_existentes = set(enviados_df["email"])

            # Leer lista de baja si se subió
            baja_existente = set()
            if baja_csv:
                baja_df = pd.read_csv(baja_csv)
                baja_existente = set(baja_df["email"])

            def update_callback(progreso_actual, total, mensaje):
                progreso.progress(progreso_actual / total)
                resultados.append(mensaje)
                resultados_box.markdown("<br>".join(resultados), unsafe_allow_html=True)

            with st.spinner("Enviando correos..."):
                resultados, enviados_exitosos = enviar_func(
                    correos_df=df,
                    html_template_str=plantilla,
                    enviados_existentes=enviados_existentes.union(baja_existente),
                    max_envios=max_envios,
                    callback=update_callback,
                )

                # Preparar CSV para descarga
                enviados_nuevos_df = pd.DataFrame({"email": list(enviados_exitosos)})
                st.download_button(
                    "📥 Descargar correos enviados",
                    enviados_nuevos_df.to_csv(index=False),
                    file_name="correos_enviados.csv",
                    mime="text/csv",
                )

            st.success("✅ Envío completado.")

with tabs[1]:
    st.markdown(
        "Sube un archivo con columnas `nombre,email` para verificar con Hunter.io"
    )

    archivo_verificar = st.file_uploader(
        "Sube CSV para verificación", type=["csv"], key="verif"
    )

    api_key = st.text_input("🔑 API Key de Hunter.io", type="password")

    if archivo_verificar and api_key:
        df_verif = pd.read_csv(archivo_verificar)
        st.dataframe(df_verif)

        if st.button("✅ Verificar correos"):
            if not acceso_autorizado:
                st.error(
                    "🚫 No tienes permiso para verificar correos. Ingresa la clave correcta en el panel lateral."
                )
                st.stop()

            verificacion_box = st.empty()

            def update_callback(actual, total, mensaje):
                verificacion_box.markdown(f"`[{actual}/{total}]` {mensaje}")

            with st.spinner("Verificando..."):
                resultado_df = verificar_correos(
                    df_verif, api_key, callback=update_callback
                )
                st.success("Verificación completada. Resultado:")
                st.dataframe(resultado_df)
                st.download_button(
                    "📥 Descargar CSV",
                    resultado_df.to_csv(index=False),
                    file_name="correos_verificados.csv",
                    mime="text/csv",
                )
