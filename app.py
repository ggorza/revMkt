import streamlit as st
from supabase import create_client, Client

# 1. Configuración de conexión y persistencia del Cliente
# Usamos session_state para que el cliente de Supabase no se recree de cero
if "supabase" not in st.session_state:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        st.session_state.supabase = create_client(url, key)
    except Exception as e:
        st.error("Error en Secrets: Asegurate de tener SUPABASE_URL y SUPABASE_KEY.")
        st.stop()

supabase: Client = st.session_state.supabase

st.set_page_config(page_title="Intercambio BA", page_icon="🤝", layout="centered")

# --- LÓGICA DE CAPTURA DE USUARIO ---
if "user" not in st.session_state:
    st.session_state.user = None

def sync_user():
    """Intenta recuperar el usuario de la sesión activa de Supabase"""
    try:
        # get_user() es lo más seguro para verificar el token actual
        res = supabase.auth.get_user()
        if res and res.user:
            return res.user
    except:
        return None
    return None

# Sincronizamos el usuario en cada ejecución del script
st.session_state.user = sync_user()

# --- PANTALLA DE LOGIN ---
if st.session_state.user is None:
    st.title("Bienvenido a Intercambio BA 🤝")
    st.subheader("Marketplace inverso para Buenos Aires")
    
    st.markdown("""
    Publicá lo que necesitás y recibí ofertas competitivas de vendedores locales[cite: 3].
    * **Registro Verificado:** Solo usuarios con Google[cite: 11].
    * **Geolocalización por Barrios:** Enfocado 100% en CABA[cite: 14].
    """)

    # URL Hardcodeada como pediste
    redirect_url = "https://revmkt.streamlit.app" 
    
    try:
        # Generamos la URL de Google Auth
        # Importante: Supabase maneja el callback internamente
        auth_res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        st.link_button("🚀 Entrar con Google", auth_res.url, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al configurar el login: {e}")

    st.info("⚠️ **Si ya te logueaste:** Por limitaciones técnicas de Streamlit, es posible que tengas que refrescar la página (F5) o tocar el botón una segunda vez para que la sesión impacte.")
    st.stop()

# --- PANEL PRINCIPAL (POST-LOGIN) ---
user = st.session_state.user
st.sidebar.success(f"Sesión: {user.email}")

if st.sidebar.button("Cerrar Sesión"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# Selección de Rol según el Brief [cite: 54]
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
        desc = st.text_area("Detalles técnicos o condiciones")
        # Barrios definidos en el alcance del MVP [cite: 14]
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
    st.caption("Respondé con ofertas para ganar el contacto[cite: 14, 67].")
    
    try:
        # Filtramos para no ver pedidos propios [cite: 13]
        res = supabase.table("requests").select("*").eq("status", "open").neq("buyer_id", user.id).execute()
        if not res.data:
            st.info("No hay pedidos de otros usuarios en este momento.")
        else:
            for p in res.data:
                with st.expander(f"📦 {p['title']} - 📍 {p['neighborhood']}"):
                    st.write(p['description'])
                    # Botón para iniciar el flujo de oferta estructurada [cite: 13]
                    if st.button("Ofertar", key=f"btn_{p['id']}"):
                        st.session_state.selected_request = p['id']
                        st.info(f"Preparando oferta para: {p['title']}")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
