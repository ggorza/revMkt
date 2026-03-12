import streamlit as st
from supabase import create_client, Client

# 1. Conexión segura usando los Secrets de Streamlit
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Intercambio BA", layout="centered")

st.title("Plataforma de Intercambio 🇦🇷")
st.markdown("---")

# --- SECCIÓN: PUBLICAR SOLICITUD (Comprador) ---
with st.expander("➕ Publicar lo que necesito", expanded=True):
    with st.form("request_form"):
        title = st.text_input("¿Qué estás buscando?", placeholder="Ej: Lavasecarropas Samsung WD106")
        desc = st.text_area("Detalles (estado, marca, modelo)")
        # Barrios sugeridos según el brief [cite: 19, 65]
        barrio = st.selectbox("Barrio de CABA", ["Palermo", "Belgrano", "Caballito", "Villa Urquiza", "Almagro", "Otros"])
        
        submitted = st.form_submit_button("Publicar Pedido")
        
        if submitted:
            if title and desc:
                # Insertamos en la tabla que creaste en Supabase [cite: 84]
                data = {
                    "title": title,
                    "description": desc,
                    "neighborhood": barrio,
                    "status": "open"
                }
                supabase.table("requests").insert(data).execute()
                st.success("¡Pedido publicado! Los vendedores pronto te enviarán ofertas.")
            else:
                st.warning("Por favor completá los campos principales.")

# --- SECCIÓN: VER PEDIDOS (Vendedor) ---
st.subheader("Pedidos Activos en tu zona")
try:
    # Traemos las solicitudes abiertas [cite: 13, 66]
    response = supabase.table("requests").select("*").eq("status", "open").order("created_at", desc=True).execute()
    requests = response.data
    
    if not requests:
        st.info("No hay pedidos abiertos en este momento.")
    else:
        for req in requests:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"### {req['title']}")
                    st.write(f"📍 {req['neighborhood']}")
                    st.caption(req['description'])
                with col2:
                    # Botón para que el vendedor envíe oferta [cite: 13, 84]
                    if st.button("Ofertar", key=req['id']):
                        st.info("Función de oferta en desarrollo...")
                st.markdown("---")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
