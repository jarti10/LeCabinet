# =============================
# 🧩 IMPORTACIÓN DE LIBRERÍAS
# =============================
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image

# =============================
# ⚙️ CONFIGURACIÓN DE LA APP
# =============================
st.set_page_config(page_title="LaCabina", layout="centered")

# =============================
# 🔐 CONECTAR CON GOOGLE SHEETS
# =============================
def conectar_hoja():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1Iq-HAZgiG4SnZdsZ020MKozUX_KUubNZ773CxVJLo3E").sheet1
    return sheet

# =============================
# 🧠 FUNCIONES DE USUARIO
# =============================
def cargar_usuarios():
    sheet = conectar_hoja()
    records = sheet.get_all_records()
    return records

def usuario_valido(username, password):
    users = cargar_usuarios()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False

def registrar_usuario(username, password, nombre, email):
    users = cargar_usuarios()
    if any(user["username"] == username for user in users):
        return False
    sheet = conectar_hoja()
    sheet.append_row([username, password, nombre, email])
    return True

# ===================================
# 🔐 SISTEMA DE LOGIN / REGISTRO
# ===================================

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
        user = st.text_input("Usuario", key="login_user")
        pwd = st.text_input("Contraseña", type="password", key="login_pwd")
        if st.button("Entrar", key="login_button"):
            if usuario_valido(user, pwd):
                st.session_state.logueado = True
                st.session_state.usuario = user
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    # ----- Pestaña Registro -----
    with tabs[1]:
        st.subheader("Registro de nuevo usuario")
        nuevo_user = st.text_input("Nuevo usuario", key="reg_user")
        nuevo_pwd = st.text_input("Contraseña", type="password", key="reg_pwd")
        nombre = st.text_input("Nombre completo", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        if st.button("Registrar", key="reg_button"):
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
    st.markdown("##")

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
    seleccion = st.selectbox("Selecciona una actividad para ver su espacio de reservas:", actividades, key="actividad_selector")

    # ---------- Crear pestañas por cada actividad ----------
    tabs = st.tabs(actividades)

    for i, actividad in enumerate(actividades):
        with tabs[i]:
            if seleccion == actividad:
                st.markdown(f"## 🗓️ Has seleccionado: **{actividad}**")
                st.info("Aquí se mostrará la interfaz de reservas para esta actividad (en desarrollo).")

    # ---------- Botón de cerrar sesión ----------
    if st.button("Cerrar sesión", key="logout_button"):
        st.session_state.logueado = False
        st.experimental_rerun()