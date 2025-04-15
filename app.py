import streamlit as st
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="LaCabina", layout="centered")

# Cargar logo
logo = Image.open("LOGO CUADRADO.jpg")

# Mostrar logo grande
st.image(logo, use_column_width=True)

# Espacio
st.markdown("##")

# Lista de actividades
actividades = [
    "Barre",
    "Embarazo",
    "Movilidad",
    "Calistenia",
    "Suelo Pélvico",
    "Stretching Global Activo"
]

# Selector
seleccion = st.selectbox("Selecciona una actividad para ver su espacio de reservas:", actividades)

# Tabs por actividad
tabs = st.tabs(actividades)

for i, actividad in enumerate(actividades):
    with tabs[i]:
        if seleccion == actividad:
            st.markdown(f"## 🗓️ Has seleccionado: **{actividad}**")
            st.info("Aquí se mostrará la interfaz de reservas para esta actividad (en desarrollo).")
        else:
            st.empty()


