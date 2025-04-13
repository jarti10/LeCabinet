import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
import io

st.set_page_config(page_title="Reserva Clase LeCabinet", layout="centered")
st.title("🧘‍♀️ App de Reservas - LeCabinet")

archivo_reservas = "reservas.csv"
archivo_espera = "lista_espera.csv"
LIMITE_PLAZAS = 7

# Actividades y horarios
horarios = {
    "Barre": [("Martes", "10h"), ("Martes", "17h"), ("Martes", "18h"), ("Martes", "19h"), ("Martes", "20h"),
              ("Miércoles", "17h"), ("Miércoles", "19h"), ("Miércoles", "20h"),
              ("Jueves", "10h"), ("Jueves", "17h"), ("Jueves", "18h"), ("Jueves", "19h"),
              ("Viernes", "17h"), ("Viernes", "18h")],
    "Embarazo": [("Martes", "11h"), ("Miércoles", "18h"), ("Jueves", "11h")],
    "Movilidad": [("Martes", "12h"), ("Jueves", "12h")],
    "Calistenia": [("Miércoles", "12h"), ("Viernes", "12h"), ("Lunes", "20h"), ("Miércoles", "20h")],
    "Stretching Global Activo": [("Lunes", "12h"), ("Lunes", "16h"), ("Lunes", "17h"), ("Lunes", "18h"), ("Martes", "16h")],
    "Suelo Pélvico": [("Miércoles", "17h"), ("Miércoles", "19h")],
    "Postparto": [("Viernes", "10h"), ("Viernes", "11h")]
}

# Cargar archivos
df_reservas = pd.read_csv(archivo_reservas) if os.path.exists(archivo_reservas) else pd.DataFrame(columns=["Nombre", "Correo", "Actividad", "Día", "Hora"])
df_espera = pd.read_csv(archivo_espera) if os.path.exists(archivo_espera) else pd.DataFrame(columns=["Nombre", "Correo", "Actividad", "Día", "Hora"])

# Tabs
pestana_publica, pestana_admin = st.tabs(["🧘 Reservar clase", "🔐 Administración"])

# === PESTAÑA PÚBLICA ===
with pestana_publica:
    st.subheader("Reserva tu Clase")
    with st.form("form_reserva"):
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo electrónico")
        actividad = st.selectbox("Actividad", list(horarios.keys()))
        opciones_dia_hora = horarios[actividad]
        dias = sorted(set(d for d, h in opciones_dia_hora))
        dia = st.selectbox("Día", dias)
        horas = [h for d, h in opciones_dia_hora if d == dia]
        hora = st.selectbox("Hora", horas)

        reservas_clase = df_reservas[(df_reservas["Actividad"] == actividad) & (df_reservas["Día"] == dia) & (df_reservas["Hora"] == hora)]
        num_reservas = len(reservas_clase)

        if num_reservas >= LIMITE_PLAZAS:
            st.warning("⛔ Clase llena. Puedes unirte a la lista de espera.")
            nombre_espera = st.text_input("Tu nombre (lista de espera)")
            correo_espera = st.text_input("Tu correo (lista de espera)")
            enviar_espera = st.form_submit_button("Unirme a la lista de espera")
            if enviar_espera and nombre_espera and correo_espera:
                nueva_espera = {"Nombre": nombre_espera, "Correo": correo_espera, "Actividad": actividad, "Día": dia, "Hora": hora}
                df_espera = pd.concat([df_espera, pd.DataFrame([nueva_espera])], ignore_index=True)
                df_espera.to_csv(archivo_espera, index=False)
                st.success("📝 Te hemos añadido a la lista de espera.")
        else:
            enviar = st.form_submit_button("Reservar")
            if enviar and nombre and correo:
                nueva_reserva = {"Nombre": nombre, "Correo": correo, "Actividad": actividad, "Día": dia, "Hora": hora}
                df_reservas = pd.concat([df_reservas, pd.DataFrame([nueva_reserva])], ignore_index=True)
                df_reservas.to_csv(archivo_reservas, index=False)
                st.success(f"Gracias {nombre}, tu plaza ha sido reservada para {actividad} el {dia} a las {hora}.")

# === PESTAÑA ADMINISTRACIÓN ===
with pestana_admin:
    st.subheader("Panel de Administración")
    admin_pw = st.text_input("Contraseña de administrador", type="password")
    if admin_pw == "admin123":
        st.success("Acceso concedido.")

        st.markdown("### 🧾 Reservas actuales")
        st.dataframe(df_reservas)

        st.markdown("### ⏳ Lista de espera")
        st.dataframe(df_espera)

        st.markdown("### 🗑️ Liberar una plaza")
        actividad_lib = st.selectbox("Actividad", df_reservas["Actividad"].unique())
        dia_lib = st.selectbox("Día", df_reservas[df_reservas["Actividad"] == actividad_lib]["Día"].unique())
        hora_lib = st.selectbox("Hora", df_reservas[(df_reservas["Actividad"] == actividad_lib) & (df_reservas["Día"] == dia_lib)]["Hora"].unique())

        if st.button("Liberar plaza"):
            df_reservas = df_reservas[~((df_reservas["Actividad"] == actividad_lib) & (df_reservas["Día"] == dia_lib) & (df_reservas["Hora"] == hora_lib))].reset_index(drop=True)
            df_reservas.to_csv(archivo_reservas, index=False)
            st.success("Plaza liberada.")

            espera = df_espera[(df_espera["Actividad"] == actividad_lib) & (df_espera["Día"] == dia_lib) & (df_espera["Hora"] == hora_lib)]
            if not espera.empty:
                persona = espera.iloc[0]
                enviar_correo(persona["Correo"], actividad_lib, dia_lib, hora_lib)
                df_espera = df_espera.drop(espera.index[0])
                df_espera.to_csv(archivo_espera, index=False)
                st.info(f"Se notificó a {persona['Nombre']} por correo.")

        st.markdown("### 📤 Exportar datos")

        # Exportar reservas
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_reservas.to_excel(writer, index=False, sheet_name="Reservas")
            writer.save()
        st.download_button("⬇️ Descargar reservas (Excel)", data=excel_buffer.getvalue(), file_name="reservas_lecabinet.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Exportar lista de espera
        excel_buffer_espera = io.BytesIO()
        with pd.ExcelWriter(excel_buffer_espera, engine='openpyxl') as writer:
            df_espera.to_excel(writer, index=False, sheet_name="Lista de Espera")
            writer.save()
        st.download_button("⬇️ Descargar lista de espera (Excel)", data=excel_buffer_espera.getvalue(), file_name="lista_espera_lecabinet.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    else:
        st.warning("Introduce la contraseña para acceder al panel de administración.")

# === FUNCION PARA ENVIAR EMAIL ===
def enviar_correo(destinatario, actividad, dia, hora):
    remitente = "lecabinetosasungunea@gmail.com"
    password = "zmtf zwfj nzyz nobo"

    msg = EmailMessage()
    msg["Subject"] = "¡Plaza disponible en LeCabinet!"
    msg["From"] = remitente
    msg["To"] = destinatario
    msg.set_content(f"Hola, se ha liberado una plaza para {actividad} el {dia} a las {hora}. ¡Apresúrate a reservar!")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remitente, password)
            smtp.send_message(msg)
    except Exception as e:
        st.error(f"Error al enviar correo: {e}")
