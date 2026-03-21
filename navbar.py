import streamlit as st

def get_base_url():
    try:
        host = st.context.headers.get("host", "")
        if "streamlit.app" in host:
            return f"https://{host}"
        else:
            return "http://localhost:8501"
    except:
        return "http://localhost:8501"

def render_navbar(active="inicio"):
    base = get_base_url()

    pages = [
        ("inicio",    "🏠 Inicio",       base + "/"),
        ("dashboard", "📡 Dashboard",    base + "/1_Dashboard"),
        ("sobre",     "👤 Sobre el TFG", base + "/2_Sobre_el_TFG"),
    ]

    nav_items = ""
    for key, label, url in pages:
        active_style = "color:#f8fafc; background:rgba(96,165,250,0.12); border:1px solid rgba(96,165,250,0.25);" if key == active else ""
        nav_items += f'<a href="{url}" target="_self" style="text-decoration:none;"><div class="nav-item" style="{active_style}">{label}</div></a>'

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@800&display=swap');

.navbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 48px;
    height: 64px;
    background: rgba(2, 8, 24, 0.92);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 0;
}}

.nav-brand {{
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-decoration: none;
    letter-spacing: -0.5px;
}}

.nav-links {{
    display: flex;
    align-items: center;
    gap: 4px;
}}

.nav-item {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    color: #94a3b8;
    padding: 7px 18px;
    border-radius: 20px;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}}

.nav-item:hover {{
    color: #f8fafc;
    background: rgba(255,255,255,0.06);
}}

.nav-spacer {{ height: 64px; }}

[data-testid="stHeader"]  {{ display: none !important; }}
[data-testid="stSidebar"] {{ display: none !important; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 0 !important; }}
</style>

<div class="navbar">
    <span class="nav-brand">🛰️ SentAI-Scan</span>
    <div class="nav-links">
        {nav_items}
    </div>
</div>
<div class="nav-spacer"></div>
""", unsafe_allow_html=True)