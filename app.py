import streamlit as st
from supabase import create_client, Client

# 1. Conexión a Supabase
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error en Secrets: Asegurate de tener SUPABASE_URL y SUPABASE_KEY configurados.")
    st.stop()

st.set_page_config(page_title="Intercambio BA", page_icon="🤝", layout="centered")

# --- GESTIÓN DE SESIÓN ---
# Intentamos obtener la sesión actual (esto captura el login después del redirect)
if "user" not in st.session_state:
    st.session_state.user = None

try:
    # Verificamos si Supabase ya tiene una sesión activa
    auth_session = supabase.auth.get_session()
    if auth_session:
        st.session_state.user = auth_session.user
except:
    pass

# --- PANTALLA DE LOGIN ---
if not st.session_state.user:
    st.title("Bienvenido a Intercambio BA 🤝")
    st.subheader("Marketplace inverso para Buenos Aires")
    
    st.markdown("""
    Publicá lo que necesitás y recibí ofertas competitivas de comercios y vecinos[cite: 3, 54].
    * **Seguro:** Acceso verificado mediante Google.
    * **Local:** Enfocado 100% en barrios de CABA[cite: 19, 54].
    """)

    # --- CAMBIAR ESTA URL POR LA TUYA ---
    # Ejemplo: "https://mi-proyecto.streamlit.app"
    redirect_url = "https://revmkt.streamlit.app" 
    
    # Generamos la URL de Google Auth
    try:
        auth_res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        st.link_button("🚀 Entrar con Google", auth_res.url, use_container_width=True)
    except Exception as e:
        st.error(f"Error al configurar el login: {e}")

    st.info("Nota: Si ya iniciaste sesión y seguís viendo esto, refrescá la página.")
    st.stop()

# --- PANEL PRINCIPAL (POST-LOGIN) ---
user = st.session_state.user
st.sidebar.success(f"Usuario: {user.email}")

if st.sidebar.button("Cerrar Sesión"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# Selección de Rol según el Brief [cite: 7, 8]
rol = st.radio(
    "¿Qué querés hacer hoy?", 
    ["🛍️ Comprar (Publicar pedido)", "💰 Vender (Ver pedidos locales)"], 
    horizontal=True
)

st.divider()

if rol == "🛍️ Comprar (Publicar pedido)":
    st.header("Publicar Solicitud")
    with st.form("form_compra", clear_on_submit=True):
        titulo = st.text_input("¿Qué buscás?", placeholder="Ej: Lavasecarropas Samsung")
        desc = st.text_area("Detalles (nuevo/usado, marca, modelo) [cite: 12]")
        barrio = st.selectbox("Barrio de búsqueda [cite: 14]", 
                             ["Palermo", "Belgrano", "Caballito", "Villa Urquiza", "Almagro", "Recoleta", "Otros"])
        
        if st.form_submit_button("Publicar"):
            if titulo and desc:
                data = {
                    "buyer_id": user.id,
                    "title": titulo,
                    "description": desc,
                    "neighborhood": barrio
                }
                supabase.table("requests").insert(data).execute()
                st.success("¡Pedido publicado!")
            else:
                st.warning("Completá los campos.")

else:
    st.header("Pedidos en Buenos Aires")
    st.caption("Ofertas competitivas para cerrar ventas[cite: 8].")
    
    try:
        # Mostramos pedidos de otros usuarios
        res = supabase.table("requests").select("*").eq("status", "open").neq("buyer_id", user.id).execute()
        if not res.data:
            st.info("No hay pedidos de otros usuarios todavía.")
        else:
            for p in res.data:
                with st.expander(f"📦 {p['title']} - 📍 {p['neighborhood']}"):
                    st.write(p['description'])
                    st.button("Ofertar", key=f"btn_{p['id']}")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
