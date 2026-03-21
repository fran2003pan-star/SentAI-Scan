import streamlit as st

def render_navbar(active="inicio"):

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@800&display=swap');

[data-testid="stHeader"] {{ display: none !important; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 10px !important; }}

/* Botón sidebar siempre visible */
[data-testid="stSidebarCollapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
}}

.navbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 48px;
    height: 64px;
    background: rgba(2, 8, 24, 0.92);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 24px;
    border-radius: 0 0 16px 16px;
}}

.nav-brand {{
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

div[data-testid="stHorizontalBlock"] button {{
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #94a3b8 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    border-radius: 20px !important;
    padding: 6px 16px !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
    height: 36px !important;
    line-height: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: 0 !important;
    width: 100% !important;
}}

div[data-testid="stHorizontalBlock"] button:hover {{
    color: #f8fafc !important;
    background: rgba(255,255,255,0.06) !important;
}}
</style>

<div class="navbar">
    <span class="nav-brand">🛰️ SentAI-Scan</span>
</div>
""", unsafe_allow_html=True)

    _, c1, c2, c3, _ = st.columns([3, 1.2, 1.2, 1.5, 3])

    active_style = "background:rgba(96,165,250,0.12);border:1px solid rgba(96,165,250,0.25);color:#f8fafc;"
    inactive_style = "background:transparent;border:1px solid transparent;color:#94a3b8;"

    with c1:
        st.markdown(f'<style>.nb1 button{{{active_style if active=="inicio" else inactive_style}}}</style><div class="nb1">', unsafe_allow_html=True)
        if st.button(" Inicio", use_container_width=True, key="nb_inicio"):
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<style>.nb2 button{{{active_style if active=="dashboard" else inactive_style}}}</style><div class="nb2">', unsafe_allow_html=True)
        if st.button(" Dashboard", use_container_width=True, key="nb_dashboard"):
            st.switch_page("pages/1_Dashboard.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown(f'<style>.nb3 button{{{active_style if active=="sobre" else inactive_style}}}</style><div class="nb3">', unsafe_allow_html=True)
        if st.button(" Sobre el TFG", use_container_width=True, key="nb_sobre"):
            st.switch_page("pages/2_Sobre_el_TFG.py")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:8px 0 28px 0;'>", unsafe_allow_html=True)