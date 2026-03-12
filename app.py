import streamlit as st
from supabase import create_client, Client

# 1. Inicialización de conexión persistente
if "supabase" not in st.session_state:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        st.session_state.supabase = create_client(url, key)
    except Exception as e:
        st.error("Error en Secrets: Revisá SUPABASE_URL y SUPABASE_KEY en Streamlit.")
        st.stop()

supabase: Client = st.session_state.supabase

st.set_page_config(page_title="Intercambio BA", page_icon="🤝", layout="centered")

# --- GESTIÓN DE SESIÓN ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- PANTALLA DE ACCESO (Login / Registro) ---
if st.session_state.user is None:
    st.title("Intercambio BA 🤝")
    st.subheader("Acceso a la plataforma")
    
    st.markdown("""
    Registrate para publicar pedidos o enviar ofertas en Buenos Aires[cite: 54].
    * **Seguro:** Tu cuenta está protegida por Supabase.
    * **Verificado:** Usamos tu email para validar las transacciones[cite: 11].
    """)

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e:
                    st.error("Email o contraseña incorrectos.")

    with tab2:
        st.info("Creá tu cuenta para empezar a operar en tu barrio[cite: 14].")
        with st.form("signup_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Contraseña (mínimo 6 caracteres)")
            if st.form_submit_button("Crear Cuenta", use_container_width=True):
                try:
                    # Registra al usuario en Supabase Auth
                    res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                    st.success("¡Cuenta creada! Ya podés ingresar desde la pestaña 'Ingresar'.")
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
    st.stop()

# --- PANEL POST-LOGIN ---
user = st.session_state.user
st.sidebar.success(f"Usuario: {user.email}")

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
    st.write("Contanos qué necesitás y los vendedores te enviarán ofertas[cite: 65].")
    
    with st.form("form_compra", clear_on_submit=True):
        titulo = st.text_input("¿Qué buscás?", placeholder="Ej: Bicicleta rodado 20")
        desc = st.text_area("Detalles (nuevo/usado, marca, modelo) [cite: 12]")
        barrio = st.selectbox("Barrio de búsqueda [cite: 14]", 
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
                    st.success("¡Pedido publicado exitosamente! [cite: 65]")
                except Exception as e:
                    st.error(f"Error al publicar: {e}")
            else:
                st.warning("Por favor, completá los campos obligatorios.")

else:
    st.header("Pedidos en Buenos Aires")
    st.caption("Respondé a las necesidades de los compradores con tus mejores ofertas[cite: 66].")
    
    try:
        # Mostramos pedidos que no sean del propio usuario [cite: 63]
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
