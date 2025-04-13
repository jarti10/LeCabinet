import streamlit as st
from datetime import date
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Reserva Clase de Barre", layout="centered")

st.title("🩰 Reserva tu Clase de Barre")
st.markdown("Por favor, completa el formulario para reservar tu clase:")

# Ruta del archivo CSV
archivo_reservas = "reservas.csv"

# Días y horarios disponibles
dias_disponibles = ["Martes", "Jueves", "Viernes"]
horarios_disponibles = ["18:00–19:00", "19:00–20:00", "20:00–21:00"]

# Formulario de reserva
with st.form("form_reserva"):
    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo electrónico")
    dia = st.selectbox("Día de la clase", dias_disponibles)
    horario = st.selectbox("Horario disponible", horarios_disponibles)
    nivel = st.radio("Nivel de experiencia", ["Principiante", "Intermedio", "Avanzado"])
    enviado = st.form_submit_button("Reservar")

    if enviado:
        if nombre and correo:
            nueva_reserva = {
                "Nombre": nombre,
                "Correo": correo,
                "Día": dia,
                "Horario": horario,
                "Nivel": nivel
            }

            # Guardar o agregar al archivo CSV
            if os.path.exists(archivo_reservas):
                df = pd.read_csv(archivo_reservas)
                df = pd.concat([df, pd.DataFrame([nueva_reserva])], ignore_index=True)
            else:
                df = pd.DataFrame([nueva_reserva])

            df.to_csv(archivo_reservas, index=False)

            st.success(f"¡Gracias, {nombre}! Tu clase fue reservada para el {dia} en el horario {horario}.")
        else:
            st.error("Por favor, completa todos los campos obligatorios.")

