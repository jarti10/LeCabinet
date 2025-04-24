# =============================
# 🧩 IMPORTACIÓN DE LIBRERÍAS
# =============================
import streamlit as st
import pandas as pd
from PIL import Image
import os

# =============================
# ⚙️ CONFIGURACIÓN DE LA APP
# =============================
st.set_page_config(page_title="LaCabina", layout="centered")

# =============================
# 📁 RUTAS Y ARCHIVOS
# =============================
DB_FILE = "usuarios.xlsx"          # Archivo Excel donde se guardan los usuarios
SHEET_NAME = "usuarios"            # Nombre de la hoja de Excel

# ========================================================
# 📄 INICIALIZACIÓN: crea la base de datos si no existe
# ========================================================
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["username", "password", "nombre", "email"])
    df_init.to_excel(DB_FILE, index=False, sheet_name=SHEET_NAME)

# =============================
# 🧠 FUNCIONES DE AUTENTICACIÓN
# =============================

# Carga los datos de usuarios desde el archivo Excel
def cargar_usuarios():
    return pd.read_excel(DB_FILE, sheet_name=SHEET_NAME)

# Verifica si un usuario y contraseña son válidos
def usuario_valido(username, password):
    df = cargar_usuarios()
    user = df[(df["username"] == username) & (df["password"] == password)]
    return not user.empty

# Registra un nuevo usuario si no existe aún
def registrar_usuario(username, password, nombre, email):
    df = cargar_usuarios()
    if username in df["username"].values:
        return False  # Usuario ya existe
    nuevo_usuario = pd.DataFrame([[username, password, nombre, email]],
                                 columns=["username", "password", "nombre", "email"])
    df = pd.concat([df, nuevo_usuario], ignore_index=True)
    df.to_excel(DB_FILE, index=False, sheet_name=SHEET_NAME)
    return True

# ===================================
# 🔐 SISTEMA DE LOGIN / REGISTRO
# ===================================

# Estado de sesión: si no está definido, lo inicializa
if "logueado" not in st.session_state:
    st.session_state.logueado = False

# ============================
# 👤 USUARIO NO LOGUEADO
# ============================
if not st.session_state.logueado:
    st.title("🔐 Bienvenido a LaCabina")

    # Tabs para login y registro
    tabs = st.tabs(["Iniciar sesión", "Registrarse"])

    # ----- Pestaña Login -----
    with tabs[0]:
        st.subheader("Iniciar sesión")
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if usuario_valido(user, pwd):
                st.session_state.logueado = True
                st.session_state.usuario = user
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    # ----- Pestaña Registro -----
    with tabs[1]:
        st.subheader("Registro de nuevo usuario")
        nuevo_user = st.text_input("Nuevo usuario")
        nuevo_pwd = st.text_input("Contraseña", type="password")
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Email")
        if st.button("Registrar"):
            if registrar_usuario(nuevo_user, nuevo_pwd, nombre, email):
                st.success("¡Usuario creado con éxito! Ahora puedes iniciar sesión.")
            else:
                st.warning("Ese nombre de usuario ya existe.")

# ================================
# ✅ USUARIO LOGUEADO (APP MAIN)
# ================================
else:
    # ---------- Mostrar logo grande ----------
    logo = Image.open("LOGO CUADRADO.jpg")
    st.image(logo, use_column_width=True)
    st.markdown("##")  # Espacio debajo del logo

    # ---------- Actividades disponibles ----------
    actividades = [
        "Barre",
        "Embarazo",
        "Movilidad",
        "Calistenia",
        "Suelo Pélvico",
        "Stretching Global Activo"
    ]

    # ---------- Selector de actividades ----------
    seleccion = st.selectbox("Selecciona una actividad para ver su espacio de reservas:", actividades)

    # ---------- Crear pestañas por cada actividad ----------
    tabs = st.tabs(actividades)

    for i, actividad in enumerate(actividades):
        with tabs[i]:
            if seleccion == actividad:
                st.markdown(f"## 🗓️ Has seleccionado: **{actividad}**")
                st.info("Aquí se mostrará la interfaz de reservas para esta actividad (en desarrollo).")
            else:
                st.empty()

    # ---------- Botón de cerrar sesión ----------
    if st.button("Cerrar sesión"):
        st.session_state.logueado = False
        st.experimental_rerun()
