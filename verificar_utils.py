import pandas as pd
import requests
import time
import os


def verificar_correos(
    df,
    api_key,
    sleep_time=1.0,
    callback=None,
):
    resultados = []

    df = df.drop_duplicates(subset=["email"])
    total = len(df)

    for i, row in enumerate(df.iterrows()):
        _, datos = row
        email = datos["email"]
        nombre = datos["nombre"]

        try:
            url = f"http://apilayer.net/api/check?access_key={api_key}&email={email}&smtp=1&format=1"
            response = requests.get(url)
            data = response.json()

            if data.get("success") is False:
                print(
                    f"⚠️ Error con {email}: {data.get('error', {}).get('info', 'Desconocido')}"
                )
                break
            else:
                resultado = (
                    "válido"
                    if data.get("format_valid", False) and data.get("smtp_check", False)
                    else "inválido"
                )

        except Exception as e:
            print(f"❌ Excepción con {email}: {e}")
            break

        if resultado == "válido":
            resultados.append({"nombre": nombre, "email": email})

        print(f"[{i+1}/{total}] {email} → {resultado}")
        if callback:
            callback(i + 1, total, f"{email} → {resultado}")

        time.sleep(sleep_time)

    resultado_df = pd.DataFrame(resultados)
    return resultado_df
