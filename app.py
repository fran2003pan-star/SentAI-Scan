import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from core.reddit_client import fetch_reddit_data
from engine.ia_model import InnoAnalyzer

# 1. CONFIGURACIÓN E INTERFAZ BASE
st.set_page_config(page_title="InnoRadar Pro", layout="wide", initial_sidebar_state="expanded")

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

local_css("style.css")
analyzer = InnoAnalyzer()

# 2. MOTOR DE PERSISTENCIA (DB)
def guardar_en_sistema(df, sub_name):
    try:
        conn = sqlite3.connect("database/radar_innovacion_ia.db")
        df['fecha_analisis'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        df['subreddit_origen'] = sub_name
        df.to_sql('analisis_reddit', conn, if_exists='append', index=False)
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error de persistencia: {e}")
        return False

def consultar_existentes(subreddit_name, limite_requerido):
    try:
        conn = sqlite3.connect("database/radar_innovacion_ia.db")
        query = f"SELECT * FROM analisis_reddit WHERE subreddit_origen = '{subreddit_name}' ORDER BY RANDOM() LIMIT {limite_requerido}"
        df_local = pd.read_sql(query, conn)
        conn.close()
        return df_local
    except:
        return pd.DataFrame()

# 3. PANEL DE CONTROL (SIDEBAR)
with st.sidebar:
    st.markdown("## 🛰️ InnoRadar Pro")
    opciones_ia = {
        "Artificial Intelligence": "ArtificialInteligence",
        "Machine Learning": "MachineLearning",
        "ChatGPT & LLMs": "ChatGPT"
    }
    seleccion = st.selectbox("Comunidad:", list(opciones_ia.keys()))
    sub = opciones_ia[seleccion]
    num = st.select_slider("Muestra:", options=[100, 500, 1000, 2000])
    lanzar = st.button("🚀 EJECUTAR ANÁLISIS")

# 4. LÓGICA DE PROCESAMIENTO Y DASHBOARD
if lanzar:
    df_local = consultar_existentes(sub, num)
    
    if len(df_local) >= num:
        st.info("⚡ Inteligencia recuperada del archivo local.")
        df_final = df_local.head(num)
    else:
        with st.spinner(f"📥 Sincronizando nuevos datos de r/{sub}..."):
            df_raw = fetch_reddit_data(sub, num)
            if df_raw is not None and not df_raw.empty:
                df_final = analyzer.process_data(df_raw)
                guardar_en_sistema(df_final, sub)
            else:
                st.error("No se detectó flujo de datos.")
                st.stop()

    # --- RENDERIZADO DEL DASHBOARD PRO ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("1. El Termómetro de Sentimiento")
    
    col_gauge, col_metrics = st.columns([1.5, 1])
    
    with col_gauge:
        avg_s = df_final['sentimiento_puntuacion'].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = avg_s,
            title = {'text': "Sentimiento Global", 'font': {'color': "#60a5fa"}},
            gauge = {
                'axis': {'range': [-1, 1]},
                'bar': {'color': "#1e71f8"},
                'steps': [
                    {'range': [-1, -0.2], 'color': '#ef4444'},
                    {'range': [-0.2, 0.2], 'color': "#e7eb14"},
                    {'range': [0.2, 1], 'color': '#22c55e'}
                ],
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_metrics:
        st.metric("Volumen", f"{len(df_final)} posts")
        st.metric("Tópico Dominante", "IA Generativa")
        st.markdown("📉 *Histórico actualizado en DB local*")
    
    st.markdown("---")
    st.header("2. Segmentación Inteligente")
    fig_scat = px.scatter(df_final, x="sentimiento_puntuacion", y="puntuacion", 
                         color="perfil_usuario", size="num_comentarios",
                         hover_name="titulo", template="plotly_dark", height=500)
    fig_scat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scat, use_container_width=True)

    st.markdown("---")
    
    # --- NIVEL 3: EVOLUCIÓN Y DETALLE ---


    st.header("3. Evolución y Detalle")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Creamos dos columnas con anchos proporcionales
    col_tabla, col_barras = st.columns([1.2, 1])

    with col_tabla:
        st.subheader("Top Mensajes de Impacto")
        # Mostramos la tabla primero para que guíe la lectura
        st.dataframe(
            df_final[['titulo', 'puntuacion', 'perfil_usuario']]
            .sort_values('puntuacion', ascending=False)
            .head(10), 
            use_container_width=True,
            hide_index=True # Limpiamos la tabla para que se vea más pro
        )

    with col_barras:
        st.subheader("Análisis de Segmentos")
        counts = df_final['perfil_usuario'].value_counts().reset_index()
        counts.columns = ['Perfil', 'Cantidad']
        
        fig_bar = px.bar(
            counts, 
            x='Cantidad', 
            y='Perfil', 
            orientation='h',
            color='Perfil',
            color_discrete_map={
                "Tecnófilos (Innovación)": "#00fbff", # Azul chillón
                "Curiosos (Herramientas/Dudas)": "#f9d71c", # Amarillo
                "Preocupados (Ética/Riesgos)": "#ff4b4b"  # Rojo
            },
            template="plotly_dark"
        )
        
        # AJUSTE CRÍTICO DE MÁRGENES para que no se vea "movido"
        fig_bar.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350, # Ajustamos altura para alinear con la tabla
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis={'title': ''}, # Quitamos títulos redundantes
            yaxis={'title': ''}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)