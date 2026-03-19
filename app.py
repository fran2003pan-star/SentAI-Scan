import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from core.reddit_client import fetch_reddit_data
from engine.ia_model import InnoAnalyzer

# ─────────────────────────────────────────────
# 1. CONFIGURACIÓN BASE
# ─────────────────────────────────────────────
st.set_page_config(page_title="SentAI-Scan", layout="wide", initial_sidebar_state="expanded")

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

local_css("style.css")
analyzer = InnoAnalyzer()

# Paleta de colores consistente para perfiles (dinámica, no hardcodeada por subreddit)
PERFIL_COLORS = {
    "Tecnófilos (Innovación)":       "#00fbff",
    "Curiosos (Herramientas/Dudas)": "#f9d71c",
    "Preocupados (Ética/Riesgos)":   "#ff4b4b"
}

# ─────────────────────────────────────────────
# 2. MOTOR DE PERSISTENCIA (DB)
# ─────────────────────────────────────────────
def guardar_en_sistema(df: pd.DataFrame, sub_name: str) -> bool:
    try:
        conn = sqlite3.connect("database/radar_innovacion_ia.db")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analisis_reddit (
                titulo TEXT,
                puntuacion INTEGER,
                num_comentarios INTEGER,
                titulo_limpio TEXT,
                cluster_id INTEGER,
                tema_cluster TEXT,
                sentimiento_vader REAL,
                sentimiento_roberta REAL,
                sentimiento_puntuacion REAL,
                fuente_sentimiento TEXT,
                perfil_usuario TEXT,
                fecha_analisis TEXT,
                subreddit_origen TEXT,
                UNIQUE(titulo, subreddit_origen)
            )
        """)
        df['fecha_analisis'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        df['subreddit_origen'] = sub_name
        for _, row in df.iterrows():
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO analisis_reddit VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, tuple(row.get(c) for c in [
                    'titulo','puntuacion','num_comentarios','titulo_limpio',
                    'cluster_id','tema_cluster','sentimiento_vader',
                    'sentimiento_roberta','sentimiento_puntuacion',
                    'fuente_sentimiento','perfil_usuario',
                    'fecha_analisis','subreddit_origen'
                ]))
            except Exception:
                continue
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error de persistencia: {e}")
        return False

def consultar_existentes(subreddit_name: str, limite_requerido: int) -> pd.DataFrame:
    try:
        conn = sqlite3.connect("database/radar_innovacion_ia.db")
        query = """
            SELECT * FROM analisis_reddit
            WHERE subreddit_origen = ?
            ORDER BY RANDOM()
            LIMIT ?
        """
        df_local = pd.read_sql(query, conn, params=(subreddit_name, limite_requerido))
        conn.close()
        return df_local
    except Exception:
        return pd.DataFrame()

def calcular_topico_dominante(df: pd.DataFrame) -> str:
    if 'tema_cluster' not in df.columns or df.empty:
        return "Sin datos"
    return df['tema_cluster'].value_counts().idxmax()


# ─────────────────────────────────────────────
# 3. PANEL DE CONTROL (SIDEBAR)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛰️ SentAI-Scan")
    st.markdown("---")
    opciones_ia = {
        "Artificial Intelligence": "ArtificialInteligence",
        "Machine Learning":        "MachineLearning",
        "ChatGPT & LLMs":          "ChatGPT"
    }
    seleccion = st.selectbox("Comunidad:", list(opciones_ia.keys()))
    sub = opciones_ia[seleccion]
    num = st.select_slider("Muestra:", options=[100, 500, 1000, 2000])
    lanzar = st.button("🚀 EJECUTAR ANÁLISIS")
    st.markdown("---")
    st.caption("SentAI-Scan · TFG 2025")


# ─────────────────────────────────────────────
# 4. LÓGICA DE PROCESAMIENTO
# ─────────────────────────────────────────────
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

    # Aseguramos tipos correctos independientemente del subreddit
    df_final['puntuacion']             = pd.to_numeric(df_final['puntuacion'],             errors='coerce').fillna(0)
    df_final['num_comentarios']        = pd.to_numeric(df_final['num_comentarios'],        errors='coerce').fillna(0)
    df_final['sentimiento_puntuacion'] = pd.to_numeric(df_final['sentimiento_puntuacion'], errors='coerce').fillna(0)

    st.markdown(f"## 📡 Dashboard — r/{sub}")
    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 1 — TERMÓMETRO DE SENTIMIENTO
    # ════════════════════════════════════════════════════════════════════════
    st.header("1. Termómetro de Sentimiento")

    col_gauge, col_metrics = st.columns([1.5, 1])

    with col_gauge:
        avg_s = df_final['sentimiento_puntuacion'].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(avg_s, 3),
            delta={'reference': 0, 'valueformat': '.3f'},
            title={'text': f"Sentimiento Global · r/{sub}", 'font': {'color': "#60a5fa", 'size': 16}},
            gauge={
                'axis': {'range': [-1, 1]},
                'bar':  {'color': "#1e71f8"},
                'steps': [
                    {'range': [-1,   -0.2], 'color': '#ef4444'},
                    {'range': [-0.2,  0.2], 'color': '#e7eb14'},
                    {'range': [0.2,   1.0], 'color': '#22c55e'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 3},
                    'thickness': 0.75,
                    'value': avg_s
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "white"},
            height=320,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_metrics:
        st.metric("📦 Volumen analizado",  f"{len(df_final)} posts")
        st.metric("🏷️ Tópico Dominante",   calcular_topico_dominante(df_final))
        st.metric("💬 Comentarios medios", f"{int(df_final['num_comentarios'].mean())}")
        st.metric("🔥 Post más viral",      f"{int(df_final['puntuacion'].max())} pts")
        if 'fuente_sentimiento' in df_final.columns:
            n_roberta = (df_final['fuente_sentimiento'] == 'RoBERTa+VADER').sum()
            st.caption(f"🤖 {n_roberta} posts analizados con RoBERTa+VADER")

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 2 — POSTS VIRALES VS SENTIMIENTO
    # ════════════════════════════════════════════════════════════════════════
    st.header("2. Posts Virales vs Sentimiento")
    st.caption("Top 15 posts por puntuación. El color indica si el post genera debate positivo, neutro o negativo.")

    top15 = (
        df_final[['titulo', 'puntuacion', 'sentimiento_puntuacion', 'perfil_usuario']]
        .sort_values('puntuacion', ascending=False)
        .head(15)
        .copy()
    )
    top15['titulo_corto'] = top15['titulo'].apply(lambda x: x[:65] + '…' if len(x) > 65 else x)

    fig_viral = px.bar(
        top15,
        x='puntuacion',
        y='titulo_corto',
        orientation='h',
        color='sentimiento_puntuacion',
        color_continuous_scale=['#ef4444', '#e7eb14', '#22c55e'],
        range_color=[-1, 1],
        hover_data={'titulo': True, 'puntuacion': True, 'perfil_usuario': True, 'titulo_corto': False},
        template='plotly_dark',
        height=520
    )
    fig_viral.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder': 'total ascending', 'title': ''},
        xaxis={'title': 'Puntuación (upvotes)'},
        coloraxis_colorbar=dict(
            title="Sentimiento",
            tickvals=[-1, 0, 1],
            ticktext=["Negativo", "Neutro", "Positivo"]
        ),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_viral, use_container_width=True)
    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 3 — MAPA DE CONTROVERSIA + RADAR
    # ════════════════════════════════════════════════════════════════════════
    st.header("3. Mapa de Controversia por Perfil")
    st.caption("¿Qué perfil genera más engagement? Cruza comentarios vs puntuación para detectar contenido polarizador.")

    col_heat, col_radar = st.columns(2)

    with col_heat:
        heat_data = (
            df_final.groupby('perfil_usuario')
            .agg(
                puntuacion_media=('puntuacion',             'mean'),
                comentarios_medios=('num_comentarios',      'mean'),
                total_posts=('titulo',                      'count')
            )
            .reset_index()
        )
        fig_heat = px.scatter(
            heat_data,
            x='puntuacion_media',
            y='comentarios_medios',
            size='total_posts',
            color='perfil_usuario',
            color_discrete_map=PERFIL_COLORS,
            text='perfil_usuario',
            template='plotly_dark',
            height=380,
            title="Engagement medio por perfil"
        )
        fig_heat.update_traces(textposition='top center', textfont_size=10)
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis_title="Puntuación media (upvotes)",
            yaxis_title="Comentarios medios",
            xaxis=dict(range=[0, heat_data['puntuacion_media'].max() * 1.4]),
            yaxis=dict(range=[0, heat_data['comentarios_medios'].max() * 1.4]),
            margin=dict(l=10, r=10, t=40, b=10),
            height=380
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_radar:
        radar_data = (
            df_final.groupby('perfil_usuario')
            .agg(
                puntuacion_media=('puntuacion',            'mean'),
                comentarios_medios=('num_comentarios',     'mean'),
                sentimiento_medio=('sentimiento_puntuacion','mean')
            )
            .reset_index()
        )
        for col in ['puntuacion_media', 'comentarios_medios']:
            max_v = radar_data[col].max()
            if max_v > 0:
                radar_data[col] = radar_data[col] / max_v
        radar_data['sentimiento_medio'] = (radar_data['sentimiento_medio'] + 1) / 2

        categorias = ['Puntuación', 'Comentarios', 'Sentimiento']
        fig_radar = go.Figure()
        for _, row in radar_data.iterrows():
            perfil  = row['perfil_usuario']
            valores = [row['puntuacion_media'], row['comentarios_medios'], row['sentimiento_medio']]
            valores += [valores[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias + [categorias[0]],
                fill='toself',
                name=perfil,
                line_color=PERFIL_COLORS.get(perfil, '#ffffff'),
                opacity=0.7
            ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1]),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            legend=dict(font=dict(size=10)),
            title="Radar de perfiles (normalizado)",
            height=380,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 4 — WORDCLOUD POR PERFIL
    # ════════════════════════════════════════════════════════════════════════
    st.header("4. Vocabulario por Perfil")
    st.caption("Las palabras más frecuentes según el tipo de usuario. Revela qué preocupa o entusiasma a cada segmento.")

    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        perfiles_unicos = df_final['perfil_usuario'].unique()
        cols_wc = st.columns(len(perfiles_unicos))

        bg_colors = {
            "Tecnófilos (Innovación)":       "#001a1a",
            "Curiosos (Herramientas/Dudas)": "#1a1a00",
            "Preocupados (Ética/Riesgos)":   "#1a0000"
        }
        wc_colormaps = {
            "Tecnófilos (Innovación)":       "cool",
            "Curiosos (Herramientas/Dudas)": "autumn",
            "Preocupados (Ética/Riesgos)":   "Reds"
        }

        col_key = 'titulo_limpio' if 'titulo_limpio' in df_final.columns else 'titulo'

        for i, perfil in enumerate(perfiles_unicos):
            texto = " ".join(
                df_final[df_final['perfil_usuario'] == perfil][col_key].dropna()
            )
            if not texto.strip():
                continue
            wc = WordCloud(
                width=500, height=300,
                background_color=bg_colors.get(perfil, "#0f172a"),
                colormap=wc_colormaps.get(perfil, "Blues"),
                max_words=60,
                collocations=False
            ).generate(texto)

            fig_wc, ax = plt.subplots(figsize=(5, 3))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            fig_wc.patch.set_facecolor('none')
            with cols_wc[i]:
                st.markdown(f"**{perfil}**")
                st.pyplot(fig_wc, use_container_width=True)
            plt.close(fig_wc)

    except ImportError:
        st.warning("⚠️ Instala wordcloud para ver esta sección: `pip install wordcloud matplotlib`")

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 5 — SEGMENTACIÓN Y DETALLE
    # ════════════════════════════════════════════════════════════════════════
    st.header("5. Segmentación y Detalle")

    col_tabla, col_barras = st.columns([1.2, 1])

    with col_tabla:
        st.subheader("Top Posts de Impacto")
        tabla = (
            df_final[['titulo', 'puntuacion', 'num_comentarios', 'perfil_usuario', 'sentimiento_puntuacion']]
            .sort_values('puntuacion', ascending=False)
            .head(10)
            .copy()
        )
        tabla['sentimiento_puntuacion'] = tabla['sentimiento_puntuacion'].round(3)
        tabla.columns = ['Título', 'Puntos', 'Comentarios', 'Perfil', 'Sentimiento']
        st.dataframe(tabla, use_container_width=True, hide_index=True)

    with col_barras:
        st.subheader("Distribución de Perfiles")
        counts = df_final['perfil_usuario'].value_counts().reset_index()
        counts.columns = ['Perfil', 'Cantidad']
        fig_bar = px.bar(
            counts,
            x='Cantidad',
            y='Perfil',
            orientation='h',
            color='Perfil',
            color_discrete_map=PERFIL_COLORS,
            template='plotly_dark'
        )
        fig_bar.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis={'title': 'Número de posts'},
            yaxis={'title': ''}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
