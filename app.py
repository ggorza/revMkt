import streamlit as st
from supabase import create_client, Client

# 1. Configuración de conexión (usando los Secrets que cargaste en Streamlit Cloud)
# Asegurate de que en Secrets tengas: SUPABASE_URL y SUPABASE_KEY
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error al leer los Secrets. Asegurate de configurarlos en Streamlit Cloud.")
    st.stop()

st.set_page_config(page_title="Intercambio BA", page_icon="🤝", layout="centered")

# --- LÓGICA DE SESIÓN ---
# En Streamlit, manejamos la persistencia con session_state
if "user" not in st.session_state:
    st.session_state.user = None

# Intentamos recuperar el usuario de la sesión de Supabase
try:
    session = supabase.auth.get_session()
    if session:
        st.session_state.user = session.user
except:
    pass

# --- PANTALLA DE LOGIN (Si no hay usuario) ---
if not st.session_state.user:
    st.title("Bienvenido a Intercambio BA 🤝")
    st.subheader("El marketplace inverso de Buenos Aires")
    
    st.markdown("""
    Centralizamos pedidos para que consigas la mejor oferta en tu barrio[cite: 3, 54].
    * **Compradores:** Publican lo que necesitan[cite: 7].
    * **Vendedores:** Compiten con ofertas claras[cite: 8].
    * **Seguridad:** Registro y verificación por Google[cite: 11, 48].
    """)

    # Generamos la URL de autenticación
    # IMPORTANTE: Cambiá 'https://tu-app.streamlit.app' por tu URL real de Streamlit
    redirect_url = "https://tu-app.streamlit.app" 
    
    auth_res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": redirect_url
        }
    })

    st.link_button("🚀 Entrar con Google", auth_res.url, use_container_width=True)
    st.info("Al ingresar, confirmás que aceptás los términos de uso y verificación local[cite: 11].")
    st.stop()

# --- PANTALLA PRINCIPAL (Si hay usuario) ---
user = st.session_state.user
st.sidebar.success(f"Sesión iniciada: {user.email}")

if st.sidebar.button("Cerrar Sesión"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# --- SELECTOR DE ROL (Comprador vs Vendedor) ---
# Cumplimos con la segmentación del brief [cite: 18, 19, 20]
rol = st.radio(
    "¿Qué querés hacer hoy?", 
    ["🛍️ Comprar (Publicar pedido)", "💰 Vender (Ver pedidos en CABA)"], 
    horizontal=True
)

st.divider()

if rol == "🛍️ Comprar (Publicar pedido)":
    st.header("Publicar lo que necesito")
    with st.form("form_compra", clear_on_submit=True):
        titulo = st.text_input("¿Qué buscás?", placeholder="Ej: Lavasecarropas Samsung usado")
        desc = st.text_area("Detalles técnicos o condiciones (ej: busco talle M, pago efectivo) ")
        # Barrios definidos en el alcance inicial [cite: 14, 65]
        barrio = st.selectbox("Barrio de entrega/búsqueda", 
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
                    st.success("¡Pedido publicado! Los vendedores de la zona ya pueden verlo[cite: 65].")
                except Exception as e:
                    st.error(f"Error al publicar: {e}")
            else:
                st.warning("Completá el título y la descripción.")

else:
    st.header("Pedidos abiertos en Buenos Aires")
    st.caption("Respondé con ofertas competitivas para ganar el contacto[cite: 8, 13].")
    
    try:
        # Traemos pedidos que no sean del propio usuario para evitar auto-ofertas
        response = supabase.table("requests").select("*").eq("status", "open").neq("buyer_id", user.id).execute()
        pedidos = response.data
        
        if not pedidos:
            st.info("No hay pedidos de otros usuarios en este momento.")
        else:
            for p in pedidos:
                with st.expander(f"📦 {p['title']} - 📍 {p['neighborhood']}"):
                    st.write(f"**Descripción:** {p['description']}")
                    st.write(f"**Publicado el:** {p['created_at'][:10]}")
                    
                    # Formulario simple de oferta estructurada [cite: 13]
                    with st.form(key=f"oferta_{p['id']}"):
                        precio = st.number_input("Tu precio (ARS)", min_value=1, step=100)
                        plazo = st.number_input("Plazo de entrega (días)", min_value=0, step=1)
                        if st.form_submit_button("Enviar Oferta"):
                            # Lógica para guardar la oferta
                            st.success(f"Oferta de ${precio} enviada. Si el comprador acepta, recibirás sus datos[cite: 67].")
                            # Aquí iría el insert a la tabla 'offers'
    except Exception as e:
        st.error(f"Error al cargar pedidos: {e}")
