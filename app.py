import streamlit as st
from supabase import create_client, Client

# 1. Configuración de conexión (Secrets de Streamlit Cloud)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error en Secrets: Asegurate de tener SUPABASE_URL y SUPABASE_KEY.")
    st.stop()

st.set_page_config(page_title="Intercambio BA", page_icon="🤝", layout="centered")

# --- GESTIÓN DE SESIÓN ---
if "user" not in st.session_state:
    st.session_state.user = None

def get_supabase_user():
    """Intenta recuperar el usuario de la sesión activa de Supabase"""
    try:
        # Esto captura la sesión si el usuario ya se logueó
        res = supabase.auth.get_user()
        if res and res.user:
            return res.user
    except:
        return None
    return None

# Actualizamos el estado del usuario
st.session_state.user = get_supabase_user()

# --- PANTALLA DE LOGIN ---
if st.session_state.user is None:
    st.title("Bienvenido a Intercambio BA 🤝")
    st.subheader("El marketplace inverso de Buenos Aires")
    
    st.markdown("""
    Publicá lo que necesitás y recibí ofertas competitivas de vendedores locales. [cite: 54, 55]
    * **Seguro:** Registro verificado mediante Google. [cite: 11, 69]
    * **Local:** Enfocado 100% en barrios de CABA. [cite: 14, 65]
    """)

    # URL de tu app (Hardcodeada como pediste)
    redirect_url = "https://revmkt.streamlit.app" 
    
    try:
        # Generamos la URL de Google Auth
        auth_res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        # Usamos el link_button para disparar el flujo
        st.link_button("🚀 Entrar con Google", auth_res.url, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al configurar el login: {e}")

    st.info("Nota: Si ya te logueaste en Google y volviste aquí, probá refrescando la página (F5).")
    st.stop()

# --- PANEL PRINCIPAL (POST-LOGIN) ---
user = st.session_state.user
st.sidebar.success(f"Usuario: {user.email}")

if st.sidebar.button("Cerrar Sesión"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# Selección de Rol según el Brief [cite: 18, 19, 20]
rol = st.radio(
    "¿Qué querés hacer hoy?", 
    ["🛍️ Comprar (Publicar pedido)", "💰 Vender (Ver pedidos locales)"], 
    horizontal=True
)

st.divider()

if rol == "🛍️ Comprar (Publicar pedido)":
    st.header("Publicar Solicitud")
    # Formulario para solicitudes con descripción y barrio [cite: 12, 65]
    with st.form("form_compra", clear_on_submit=True):
        titulo = st.text_input("¿Qué buscás?", placeholder="Ej: Lavasecarropas Samsung")
        desc = st.text_area("Detalles (nuevo/usado, marca, modelo)")
        barrio = st.selectbox("Barrio de búsqueda", 
                             ["Palermo", "Belgrano", "Caballito", "Villa Urquiza", "Almagro", "Recoleta", "Otros"])
        
        if st.form_submit_button("Publicar"):
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
                    st.success("¡Pedido publicado!")
                except Exception as e:
                    st.error(f"Error al publicar: {e}")
            else:
                st.warning("Completá los campos obligatorios.")

else:
    st.header("Pedidos en Buenos Aires")
    st.caption("Ofertas competitivas para cerrar ventas rápidas. [cite: 3, 13]")
    
    try:
        # Mostramos pedidos de otros usuarios [cite: 13, 66]
        res = supabase.table("requests").select("*").eq("status", "open").neq("buyer_id", user.id).execute()
        if not res.data:
            st.info("No hay pedidos de otros usuarios todavía.")
        else:
            for p in res.data:
                with st.expander(f"📦 {p['title']} - 📍 {p['neighborhood']}"):
                    st.write(p['description'])
                    # Botón para iniciar el flujo de oferta estructurada [cite: 13, 66]
                    if st.button("Ofertar", key=f"btn_{p['id']}"):
                        st.info("Formulario de oferta estructurada próximamente.")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
