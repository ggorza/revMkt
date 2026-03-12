import streamlit as st
from supabase import create_client, Client

# 1. Conexión a Supabase (usando tus Secrets)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error en Secrets: Revisá SUPABASE_URL y SUPABASE_KEY en Streamlit Cloud.")
    st.stop()

st.set_page_config(page_title="Intercambio BA", page_icon="🤝")

# --- GESTIÓN DE SESIÓN ---
if "user" not in st.session_state:
    st.session_state.user = None

def check_session():
    """Intenta recuperar la sesión de Supabase de forma robusta"""
    try:
        # Esto intenta capturar la sesión si el usuario viene de un link de mail
        res = supabase.auth.get_user()
        if res and res.user:
            return res.user
    except:
        return None
    return None

# Sincronizamos usuario
st.session_state.user = check_session()

# --- PANTALLA DE LOGIN (Si no hay sesión) ---
if st.session_state.user is None:
    st.title("Intercambio BA 🤝")
    st.subheader("Acceso a la plataforma")

    tab1, tab2 = st.tabs(["📧 Magic Link (Recomendado)", "🌐 Google Login"])

    with tab1:
        st.write("Te mandamos un link a tu mail para entrar sin contraseña.")
        email_input = st.text_input("Tu email", placeholder="ejemplo@gmail.com")
        if st.button("Enviar link de acceso"):
            if email_input:
                res = supabase.auth.sign_in_with_otp({"email": email_input})
                st.success(f"¡Link enviado a {email_input}! Revisá tu bandeja de entrada (y spam).")
            else:
                st.warning("Ingresá un email válido.")

    with tab2:
        st.write("Si el login de Google te da problemas, usá el Magic Link.")
        # Hardcodeado como pediste
        redirect_url = "https://revmkt.streamlit.app"
        auth_res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": redirect_url}
        })
        st.link_button("🚀 Intentar con Google", auth_res.url)

    st.stop()

# --- PANEL POST-LOGIN (Si el usuario ya entró) ---
user = st.session_state.user
st.sidebar.success(f"Logueado: {user.email}")

if st.sidebar.button("Cerrar Sesión"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# Selección de Rol según el Brief [cite: 19, 20]
rol = st.radio(
    "¿Qué querés hacer?", 
    ["🛍️ Comprar (Publicar pedido)", "💰 Vender (Ver pedidos locales)"], 
    horizontal=True
)

st.divider()

if rol == "🛍️ Comprar (Publicar pedido)":
    st.header("Publicar Solicitud")
    with st.form("form_compra", clear_on_submit=True):
        titulo = st.text_input("¿Qué buscás?", placeholder="Ej: Lavasecarropas Samsung")
        desc = st.text_area("Detalles técnicos o condiciones")
        barrio = st.selectbox("Barrio de búsqueda", 
                             ["Palermo", "Belgrano", "Caballito", "Villa Urquiza", "Almagro", "Recoleta", "Otros"])
        
        if st.form_submit_button("Publicar Pedido"):
            if titulo and desc:
                try:
                    data = {
                        "buyer_id": user.id,
                        "title": titulo,
                        "description": desc,
                        "neighborhood": barrio,
                        "status": "open"
                    }
                    supabase.table("requests").insert(data).execute()
                    st.success("¡Pedido publicado exitosamente!")
                except Exception as e:
                    st.error(f"Error al publicar: {e}")
            else:
                st.warning("Completá los campos obligatorios.")

else:
    st.header("Pedidos en Buenos Aires")
    st.caption("Respondé a las necesidades de los compradores.")
    
    try:
        # Mostramos pedidos que no sean del propio usuario [cite: 54, 65]
        res = supabase.table("requests").select("*").eq("status", "open").neq("buyer_id", user.id).execute()
        if not res.data:
            st.info("No hay pedidos de otros usuarios en este momento.")
        else:
            for p in res.data:
                with st.expander(f"📦 {p['title']} - 📍 {p['neighborhood']}"):
                    st.write(p['description'])
                    if st.button("Ofertar", key=f"btn_{p['id']}"):
                        st.info("Estamos habilitando el panel de ofertas estructuradas...")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
