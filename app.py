import streamlit as st
import pandas as pd
from correo_utils import enviar_correos as enviar_func
from verificar_utils import verificar_correos

st.set_page_config(page_title="PrometeonMailer", page_icon="📧", layout="centered")

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

        if st.button("📨 Enviar correos"):
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
                enviar_func(
                    correos_df=df,
                    html_template_str=plantilla,
                    enviados_existentes=enviados_existentes.union(baja_existente),
                    max_envios=50,
                    callback=update_callback,
                )

                # Preparar CSV para descarga
                enviados_nuevos_df = pd.DataFrame(
                    {
                        "email": list(
                            enviados_existentes.union(
                                {row["email"] for _, row in df.iterrows()}
                            )
                        )
                    }
                )
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
            with st.spinner("Verificando..."):
                resultado_df = verificar_correos(df_verif, api_key)
                st.success("Verificación completada. Resultado:")
                st.dataframe(resultado_df)
                st.download_button(
                    "📥 Descargar CSV",
                    resultado_df.to_csv(index=False),
                    file_name="correos_verificados.csv",
                    mime="text/csv",
                )
