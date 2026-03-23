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
st.set_page_config(page_title="SentAI-Scan", layout="wide", initial_sidebar_state="collapsed")
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from navbar import render_navbar
render_navbar(active="dashboard")

st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* Card del panel de control */
.panel-card {
    background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.08));
    border: 1px solid rgba(96,165,250,0.2);
    border-radius: 16px;
    padding: 20px 24px 24px 24px;
    margin-bottom: 28px;
}
.panel-label {
    font-size: 0.78rem;
    color: #60a5fa;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
    font-weight: 600;
}

/* Botón analizar en rojo — solo el de la clase btn-red */
.btn-red button {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(239,68,68,0.3) !important;
    transition: all 0.2s ease !important;
}
.btn-red button:hover {
    box-shadow: 0 0 30px rgba(239,68,68,0.5) !important;
    transform: scale(1.02) !important;
}
</style>
""", unsafe_allow_html=True)

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

local_css("style.css")
analyzer = InnoAnalyzer()

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
                titulo TEXT, puntuacion INTEGER, num_comentarios INTEGER,
                titulo_limpio TEXT, cluster_id INTEGER, tema_cluster TEXT,
                sentimiento_vader REAL, sentimiento_roberta REAL,
                sentimiento_puntuacion REAL, fuente_sentimiento TEXT,
                perfil_usuario TEXT, fecha_analisis TEXT, subreddit_origen TEXT,
                UNIQUE(titulo, subreddit_origen)
            )
        """)
        df['fecha_analisis'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        df['subreddit_origen'] = sub_name
        for _, row in df.iterrows():
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO analisis_reddit VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, tuple(row.get(c) for c in [
                    'titulo','puntuacion','num_comentarios','titulo_limpio',
                    'cluster_id','tema_cluster','sentimiento_vader','sentimiento_roberta',
                    'sentimiento_puntuacion','fuente_sentimiento','perfil_usuario',
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
        query = "SELECT * FROM analisis_reddit WHERE subreddit_origen = ? ORDER BY RANDOM() LIMIT ?"
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
# 3. INTERPRETACIONES AUTOMÁTICAS
# ─────────────────────────────────────────────
def interpretar_sentimiento(score: float) -> tuple:
    if score > 0.5:
        return "La comunidad muestra un sentimiento **muy positivo**. Predomina el entusiasmo y la innovación.", "#22c55e", "🟢"
    elif score > 0.2:
        return "La comunidad muestra un sentimiento **positivo**. El optimismo supera a la preocupación.", "#86efac", "🟢"
    elif score > 0.05:
        return "La comunidad muestra un sentimiento **levemente positivo**. El debate es equilibrado con ligero optimismo.", "#e7eb14", "🟡"
    elif score > -0.05:
        return "La comunidad muestra un sentimiento **neutro**. Hay debate equilibrado sin tendencia clara.", "#e7eb14", "🟡"
    elif score > -0.2:
        return "La comunidad muestra un sentimiento **levemente negativo**. Predomina el escepticismo y la cautela.", "#fca5a5", "🔴"
    elif score > -0.5:
        return "La comunidad muestra un sentimiento **negativo**. La preocupación y la crítica son dominantes.", "#ef4444", "🔴"
    else:
        return "La comunidad muestra un sentimiento **muy negativo**. El rechazo y la alarma son la tónica general.", "#b91c1c", "🔴"

def interpretar_perfil_dominante(df: pd.DataFrame) -> str:
    if 'perfil_usuario' not in df.columns or df.empty:
        return ""
    perfil = df['perfil_usuario'].value_counts().idxmax()
    pct = round(df['perfil_usuario'].value_counts(normalize=True).max() * 100)
    interpretaciones = {
        "Tecnófilos (Innovación)": f"El **{pct}%** de los posts proviene de usuarios entusiastas de la tecnología. La comunidad está orientada hacia la innovación y los avances.",
        "Curiosos (Herramientas/Dudas)": f"El **{pct}%** de los posts son de usuarios explorando herramientas y resolviendo dudas. Es una comunidad de aprendizaje activo.",
        "Preocupados (Ética/Riesgos)": f"El **{pct}%** de los posts reflejan preocupación por riesgos y ética. El debate crítico domina esta comunidad."
    }
    return interpretaciones.get(perfil, "")

def interpretar_controversia(heat_data: pd.DataFrame) -> str:
    if heat_data.empty:
        return ""
    perfil_max_comments = heat_data.loc[heat_data['comentarios_medios'].idxmax(), 'perfil_usuario']
    perfil_max_score = heat_data.loc[heat_data['puntuacion_media'].idxmax(), 'perfil_usuario']
    if perfil_max_comments == perfil_max_score:
        return f"Los posts de **{perfil_max_comments}** generan más upvotes Y más comentarios. Son el segmento más influyente."
    else:
        return f"Los posts de **{perfil_max_score}** reciben más upvotes, pero los de **{perfil_max_comments}** generan más debate en comentarios."

# ─────────────────────────────────────────────
# 4. PANEL DE CONTROL
# ─────────────────────────────────────────────
st.markdown('<div class="panel-card"><div class="panel-label">⚙️ Panel de Control</div>', unsafe_allow_html=True)

opciones_ia = {
    "Artificial Intelligence": "ArtificialInteligence",
    "Machine Learning":        "MachineLearning",
    "ChatGPT & LLMs":          "ChatGPT"
}

col_com, col_muestra, col_filtro, col_btn = st.columns([2, 2, 3, 1.2])

with col_com:
    seleccion = st.selectbox(" Comunidad", list(opciones_ia.keys()), key="sel_comunidad")
    sub = opciones_ia[seleccion]

with col_muestra:
    num = st.select_slider(" Muestra", options=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000], key="sel_muestra")

with col_filtro:
    filtro_perfil = st.multiselect(
        " Filtrar perfiles",
        options=["Tecnófilos (Innovación)", "Curiosos (Herramientas/Dudas)", "Preocupados (Ética/Riesgos)"],
        default=["Tecnófilos (Innovación)", "Curiosos (Herramientas/Dudas)", "Preocupados (Ética/Riesgos)"],
        key="sel_filtro"
    )

with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="btn-red">', unsafe_allow_html=True)
    lanzar = st.button(" Analizar", use_container_width=True, key="btn_analizar")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 5. HEADER PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
    <div class="main-header">
        <div style='display:flex; align-items:center; gap:16px;'>
            <span style='font-size:3rem;'></span>
            <div>
                <h1 style='margin:0; font-size:2.2rem;'>SentAI-Scan</h1>
                <p style='margin:0; color:#94a3b8; font-size:1rem;'>
                    Escáner de Sentimiento en Comunidades de IA · Powered by VADER & RoBERTa
                </p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 6. LÓGICA DE PROCESAMIENTO
# ─────────────────────────────────────────────
if lanzar:
    df_local = consultar_existentes(sub, num)

    if len(df_local) >= num:
        st.success(" Inteligencia recuperada del archivo local.")
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

    df_final['puntuacion']             = pd.to_numeric(df_final['puntuacion'],             errors='coerce').fillna(0)
    df_final['num_comentarios']        = pd.to_numeric(df_final['num_comentarios'],        errors='coerce').fillna(0)
    df_final['sentimiento_puntuacion'] = pd.to_numeric(df_final['sentimiento_puntuacion'], errors='coerce').fillna(0)

    if filtro_perfil:
        df_filtrado = df_final[df_final['perfil_usuario'].isin(filtro_perfil)]
    else:
        df_filtrado = df_final

    if df_filtrado.empty:
        st.warning("No hay datos para los perfiles seleccionados.")
        st.stop()

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 1 — TERMÓMETRO
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("### 1. Termómetro de Sentimiento")
    st.caption("Índice de polaridad global de la comunidad. Rango de -1 (muy negativo) a +1 (muy positivo).")

    col_gauge, col_metrics = st.columns([1.5, 1])
    avg_s = df_filtrado['sentimiento_puntuacion'].mean()

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(avg_s, 3),
            delta={'reference': 0, 'valueformat': '.3f'},
            title={'text': f"Sentimiento Global · r/{sub}", 'font': {'color': "#60a5fa", 'size': 16}},
            gauge={
                'axis': {'range': [-1, 1]},
                'bar':  {'color': "#1e71f8"},
                'steps': [
                    {'range': [-1, -0.2], 'color': '#ef4444'},
                    {'range': [-0.2, 0.2], 'color': '#e7eb14'},
                    {'range': [0.2, 1.0],  'color': '#22c55e'}
                ],
                'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.75, 'value': avg_s}
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"},
            height=320, margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        texto_interp, color_interp, emoji_interp = interpretar_sentimiento(avg_s)
        st.markdown(f"""
            <div style='background:rgba(255,255,255,0.05); border-left: 3px solid {color_interp};
                border-radius:8px; padding:12px 16px; margin-top:8px;'>
                {emoji_interp} {texto_interp}
            </div>
        """, unsafe_allow_html=True)

    with col_metrics:
        st.metric(" Volumen analizado",  f"{len(df_filtrado)} posts")
        st.metric(" Tópico Dominante",   calcular_topico_dominante(df_filtrado))
        st.metric(" Comentarios medios", f"{int(df_filtrado['num_comentarios'].mean())}")
        st.metric(" Post más viral",      f"{int(df_filtrado['puntuacion'].max())} pts")
        if 'fuente_sentimiento' in df_filtrado.columns:
            n_roberta = (df_filtrado['fuente_sentimiento'] == 'RoBERTa+VADER').sum()
            st.caption(f"🤖 {n_roberta} posts analizados con RoBERTa+VADER")
        interp_perfil = interpretar_perfil_dominante(df_filtrado)
        if interp_perfil:
            st.markdown(f"""
                <div style='background:rgba(255,255,255,0.05); border-radius:8px;
                    padding:12px 16px; margin-top:12px; font-size:0.9rem; color:#cbd5e1;'>
                    💡 {interp_perfil}
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 2 — POSTS VIRALES
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("### 2. Posts Virales vs Sentimiento")
    st.caption("Top 15 posts por puntuación. El color indica si el post genera debate positivo, neutro o negativo.")

    top15 = (
        df_filtrado[['titulo', 'puntuacion', 'sentimiento_puntuacion', 'perfil_usuario']]
        .sort_values('puntuacion', ascending=False).head(15).copy()
    )
    top15['titulo_corto'] = top15['titulo'].apply(lambda x: x[:65] + '…' if len(x) > 65 else x)

    fig_viral = px.bar(
        top15, x='puntuacion', y='titulo_corto', orientation='h',
        color='sentimiento_puntuacion',
        color_continuous_scale=['#ef4444', '#e7eb14', '#22c55e'],
        range_color=[-1, 1],
        hover_data={'titulo': True, 'puntuacion': True, 'perfil_usuario': True, 'titulo_corto': False},
        template='plotly_dark', height=520
    )
    fig_viral.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder': 'total ascending', 'title': ''},
        xaxis={'title': 'Puntuación (upvotes)'},
        coloraxis_colorbar=dict(title="Sentimiento", tickvals=[-1, 0, 1], ticktext=["Negativo", "Neutro", "Positivo"]),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_viral, use_container_width=True)

    top_post = top15.iloc[0]
    sent_top = top_post['sentimiento_puntuacion']
    sent_label = "positivo 🟢" if sent_top > 0.1 else ("negativo 🔴" if sent_top < -0.1 else "neutro 🟡")
    st.markdown(f"""
        <div style='background:rgba(255,255,255,0.05); border-left: 3px solid #60a5fa;
            border-radius:8px; padding:12px 16px; margin-top:8px; font-size:0.9rem; color:#cbd5e1;'>
            💡 El post más viral es <b>"{top_post['titulo'][:70]}..."</b>
            con <b>{int(top_post['puntuacion'])} upvotes</b> y sentimiento {sent_label}.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 3 — MAPA DE CONTROVERSIA
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("### 3.  Mapa de Controversia por Perfil")
    st.caption("¿Qué perfil genera más engagement? Cruza comentarios vs puntuación para detectar contenido polarizador.")

    col_heat, col_radar = st.columns(2)
    heat_data = (
        df_filtrado.groupby('perfil_usuario')
        .agg(puntuacion_media=('puntuacion','mean'), comentarios_medios=('num_comentarios','mean'), total_posts=('titulo','count'))
        .reset_index()
    )

    with col_heat:
        fig_heat = px.scatter(
            heat_data, x='puntuacion_media', y='comentarios_medios',
            size='total_posts', color='perfil_usuario',
            color_discrete_map=PERFIL_COLORS, text='perfil_usuario',
            template='plotly_dark', height=380, title="Engagement medio por perfil"
        )
        fig_heat.update_traces(textposition='top center', textfont_size=10)
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(title="Puntuación media", range=[0, heat_data['puntuacion_media'].max() * 1.4]),
            yaxis=dict(title="Comentarios medios", range=[0, heat_data['comentarios_medios'].max() * 1.4]),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_radar:
        radar_data = (
            df_filtrado.groupby('perfil_usuario')
            .agg(puntuacion_media=('puntuacion','mean'), comentarios_medios=('num_comentarios','mean'), sentimiento_medio=('sentimiento_puntuacion','mean'))
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
            perfil = row['perfil_usuario']
            valores = [row['puntuacion_media'], row['comentarios_medios'], row['sentimiento_medio']]
            fig_radar.add_trace(go.Scatterpolar(
                r=valores + [valores[0]], theta=categorias + [categorias[0]],
                fill='toself', name=perfil,
                line_color=PERFIL_COLORS.get(perfil, '#ffffff'), opacity=0.7
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1]), bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'},
            legend=dict(font=dict(size=10)), title="Radar de perfiles (normalizado)",
            height=380, margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    interp_cont = interpretar_controversia(heat_data)
    if interp_cont:
        st.markdown(f"""
            <div style='background:rgba(255,255,255,0.05); border-left: 3px solid #a78bfa;
                border-radius:8px; padding:12px 16px; margin-top:8px; font-size:0.9rem; color:#cbd5e1;'>
                💡 {interp_cont}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 4 — WORDCLOUD
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("### 4.  Vocabulario por Perfil")
    st.caption("Las palabras más frecuentes según el tipo de usuario. Revela qué preocupa o entusiasma a cada segmento.")

    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        perfiles_unicos = df_filtrado['perfil_usuario'].unique()
        cols_wc = st.columns(len(perfiles_unicos))
        bg_colors = {"Tecnófilos (Innovación)": "#001a1a", "Curiosos (Herramientas/Dudas)": "#1a1a00", "Preocupados (Ética/Riesgos)": "#1a0000"}
        wc_colormaps = {"Tecnófilos (Innovación)": "cool", "Curiosos (Herramientas/Dudas)": "autumn", "Preocupados (Ética/Riesgos)": "Reds"}
        col_key = 'titulo_limpio' if 'titulo_limpio' in df_filtrado.columns else 'titulo'

        for i, perfil in enumerate(perfiles_unicos):
            texto = " ".join(df_filtrado[df_filtrado['perfil_usuario'] == perfil][col_key].dropna())
            if not texto.strip():
                continue
            wc = WordCloud(
                width=500, height=300,
                background_color=bg_colors.get(perfil, "#0f172a"),
                colormap=wc_colormaps.get(perfil, "Blues"),
                max_words=60, collocations=False
            ).generate(texto)
            fig_wc, ax = plt.subplots(figsize=(5, 3))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            fig_wc.patch.set_facecolor('none')
            with cols_wc[i]:
                st.markdown(f"** {perfil}**")
                st.pyplot(fig_wc, use_container_width=True)
            plt.close(fig_wc)

    except ImportError:
        st.warning("⚠️ Instala wordcloud: `pip install wordcloud matplotlib`")

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 5 — SEGMENTACIÓN Y DETALLE
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("### 5.  Segmentación y Detalle")

    col_tabla, col_barras = st.columns([1.2, 1])

    with col_tabla:
        st.subheader("Top Posts de Impacto")
        tabla = (
            df_filtrado[['titulo', 'puntuacion', 'num_comentarios', 'perfil_usuario', 'sentimiento_puntuacion']]
            .sort_values('puntuacion', ascending=False).head(10).copy()
        )
        tabla['sentimiento_puntuacion'] = tabla['sentimiento_puntuacion'].round(3)
        tabla.columns = ['Título', 'Puntos', 'Comentarios', 'Perfil', 'Sentimiento']
        st.dataframe(tabla, use_container_width=True, hide_index=True)

    with col_barras:
        st.subheader("Distribución de Perfiles")
        counts = df_filtrado['perfil_usuario'].value_counts().reset_index()
        counts.columns = ['Perfil', 'Cantidad']
        fig_bar = px.bar(
            counts, x='Cantidad', y='Perfil', orientation='h',
            color='Perfil', color_discrete_map=PERFIL_COLORS, template='plotly_dark'
        )
        fig_bar.update_layout(
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            xaxis={'title': 'Número de posts'}, yaxis={'title': ''}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SECCIÓN 6 — EXPORTAR DATOS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("### 6.  Exportar Datos")
    st.caption("Descarga el dataset analizado para uso externo o investigación.")

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    csv_completo = df_filtrado.to_csv(index=False).encode('utf-8')
    with col_exp1:
        st.download_button(
            label="📄 Dataset completo (CSV)",
            data=csv_completo,
            file_name=f"sentai_{sub}_{num}posts.csv",
            mime="text/csv",
            use_container_width=True
        )

    top_export = df_filtrado.sort_values('puntuacion', ascending=False).head(100)
    csv_top = top_export.to_csv(index=False).encode('utf-8')
    with col_exp2:
        st.download_button(
            label="🔥 Top 100 posts (CSV)",
            data=csv_top,
            file_name=f"sentai_{sub}_top100.csv",
            mime="text/csv",
            use_container_width=True
        )

    resumen = df_filtrado.groupby('perfil_usuario').agg(
        total_posts=('titulo', 'count'),
        puntuacion_media=('puntuacion', 'mean'),
        comentarios_medios=('num_comentarios', 'mean'),
        sentimiento_medio=('sentimiento_puntuacion', 'mean')
    ).round(3).reset_index()
    csv_resumen = resumen.to_csv(index=False).encode('utf-8')
    with col_exp3:
        st.download_button(
            label="📊 Resumen por perfil (CSV)",
            data=csv_resumen,
            file_name=f"sentai_{sub}_resumen_perfiles.csv",
            mime="text/csv",
            use_container_width=True
        )