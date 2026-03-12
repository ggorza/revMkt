import streamlit as st
from supabase import create_client, Client

# 1. Configuración de conexión (usando tus Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Intercambio BA", page_icon="🤝")

# --- LÓGICA DE AUTENTICACIÓN ---
# Intentamos recuperar la sesión actual
user = supabase.auth.get_user()

if not user:
    # --- PANTALLA DE BIENVENIDA (Sin Login) ---
    st.title("Bienvenido a Intercambio BA 🇦🇷")
    st.subheader("Conectamos tus necesidades con ofertas locales.")
    
    st.markdown("""
    En esta plataforma podés:
    * **Publicar** lo que necesitás comprar.
    * **Recibir ofertas** de vendedores de tu barrio[cite: 13].
    * **Ahorrar tiempo y dinero** con ofertas competitivas[cite: 7].
    """)

    if st.button("🚀 Entrar con Google"):
        # El flujo de OAuth de Supabase
        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "https://tu-app-en-streamlit.streamlit.app" # <--- CAMBIAR POR TU URL REAL
            }
        })
        # Redirigimos al usuario a la URL de Google
        st.write(f"Redirigiendo a Google... [Si no carga, click acá]({res.url})")
    
    st.stop()

# --- SI ESTAMOS LOGUEADOS ---
email_usuario = user.user.email
st.sidebar.success(f"Logueado como: {email_usuario}")

if st.sidebar.button("Cerrar Sesión"):
    supabase.auth.sign_out()
    st.rerun()

# --- SELECTOR DE ROL (Comprador vs Vendedor) ---
rol = st.radio("¿Qué querés hacer?", ["Comprar (Publicar pedido)", "Vender (Ver pedidos locales)"], horizontal=True)

st.divider()

if rol == "Comprar (Publicar pedido)":
    st.header("🛍️ Publicar Solicitud")
    with st.form("form_compra"):
        titulo = st.text_input("¿Qué buscás?", placeholder="Ej: Bicicleta rodado 20")
        desc = st.text_area("Detalles técnicos o estado")
        barrio = st.selectbox("Tu Barrio", ["Palermo", "Belgrano", "Caballito", "Villa Urquiza", "Almagro", "Otros"])
        
        if st.form_submit_button("Publicar Pedido"):
            # Insertamos en Supabase incluyendo el ID del usuario logueado
            data = {
                "buyer_id": user.user.id,
                "title": titulo,
                "description": desc,
                "neighborhood": barrio
            }
            supabase.table("requests").insert(data).execute()
            st.success("¡Pedido publicado! Los vendedores lo verán en su panel.")

else:
    st.header("💰 Panel para Vendedores")
    st.info("Mostrando pedidos abiertos en Buenos Aires[cite: 19].")
    
    # Traemos los pedidos de otros usuarios
    pedidos = supabase.table("requests").select("*").eq("status", "open").execute()
    
    if not pedidos.data:
        st.write("No hay pedidos abiertos en este momento.")
    else:
        for p in pedidos.data:
            with st.expander(f"{p['title']} - 📍 {p['neighborhood']}"):
                st.write(p['description'])
                st.button("Enviar Oferta", key=p['id']) # Próximo paso: Formulario de oferta [cite: 13]
