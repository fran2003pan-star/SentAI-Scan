import streamlit as st

st.set_page_config(
    page_title="SentAI-Scan",
    layout="wide",
    initial_sidebar_state="collapsed"
)
from navbar import render_navbar
render_navbar(active="inicio")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=Syne:wght@700;800&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #020818 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"]  { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

#particle-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
    pointer-events: none;
}

.landing-wrap { position: relative; z-index: 1; }

.hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 100px 40px 20px;
}

.hero-badge {
    display: inline-block;
    background: rgba(96,165,250,0.1);
    border: 1px solid rgba(96,165,250,0.3);
    border-radius: 50px;
    padding: 6px 20px;
    font-size: 0.8rem;
    color: #60a5fa;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 28px;
    animation: fadeDown 0.8s ease forwards;
    opacity: 0;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3.5rem, 8vw, 7rem);
    font-weight: 800;
    line-height: 1;
    margin-bottom: 12px;
    animation: fadeDown 0.8s 0.15s ease forwards;
    opacity: 0;
}

.hero-title .grad {
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-title .white { color: #f8fafc; }

.hero-sub {
    font-size: clamp(1rem, 2vw, 1.3rem);
    color: #94a3b8;
    max-width: 600px;
    line-height: 1.7;
    margin-bottom: 48px;
    animation: fadeDown 0.8s 0.3s ease forwards;
    opacity: 0;
}

.stats-bar {
    display: flex;
    justify-content: center;
    gap: 60px;
    padding: 40px;
    border-top: 1px solid rgba(255,255,255,0.06);
    animation: fadeUp 0.8s 0.6s ease forwards;
    opacity: 0;
}

.stat-item { text-align: center; }

.stat-number {
    font-family: 'Syne', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 0.85rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

.how-section {
    padding: 80px 40px 40px;
    max-width: 1100px;
    margin: 0 auto;
    animation: fadeUp 0.8s 0.7s ease forwards;
    opacity: 0;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    color: #f8fafc;
    text-align: center;
    margin-bottom: 60px;
}

.section-title span {
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.steps-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}

.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 32px 28px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.step-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #f472b6);
    opacity: 0;
    transition: opacity 0.3s;
}

.step-card:hover { transform: translateY(-4px); border-color: rgba(96,165,250,0.2); }
.step-card:hover::before { opacity: 1; }

.step-number {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: rgba(96,165,250,0.15);
    line-height: 1;
    margin-bottom: 16px;
}

.step-icon { font-size: 2rem; margin-bottom: 12px; }
.step-title { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 10px; }
.step-desc { font-size: 0.9rem; color: #64748b; line-height: 1.6; }

.tech-section {
    padding: 60px 40px 80px;
    max-width: 1100px;
    margin: 0 auto;
    animation: fadeUp 0.8s 0.8s ease forwards;
    opacity: 0;
}

.tech-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

.tech-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: all 0.3s ease;
}

.tech-card:hover {
    background: rgba(96,165,250,0.05);
    border-color: rgba(96,165,250,0.2);
    transform: translateY(-2px);
}

.tech-icon { font-size: 2rem; margin-bottom: 10px; }
.tech-name { font-size: 0.95rem; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
.tech-desc { font-size: 0.78rem; color: #64748b; }

@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 40px rgba(139,92,246,0.3); }
    50%       { box-shadow: 0 0 80px rgba(139,92,246,0.6); }
}

.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    border: none !important;
    color: white !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    font-size: 1.15rem !important;
    padding: 18px 52px !important;
    transition: all 0.3s ease !important;
    animation: pulse-glow 3s ease-in-out infinite !important;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 0 60px rgba(139,92,246,0.6) !important;
}

.cta-center {
    display: flex;
    justify-content: center;
    padding-bottom: 20px;
    animation: fadeDown 0.8s 0.45s ease forwards;
    opacity: 0;
}
</style>

<canvas id="particle-canvas"></canvas>

<div class="landing-wrap">
  <div class="hero">
    <div class="hero-badge">🛰️ &nbsp; TFG · Análisis de Sentimiento con IA</div>
    <div class="hero-title">
      <span class="grad">SentAI</span><span class="white">-Scan</span>
    </div>
    <p class="hero-sub">
      Escáner inteligente de sentimiento en comunidades de Reddit.<br>
      Detecta tendencias, perfiles y emociones en posts sobre IA
    </p>
  </div>
</div>

<script>
const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');
let particles = [];
let W = canvas.width  = window.innerWidth;
let H = canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
});

for (let i = 0; i < 80; i++) {
    particles.push({
        x: Math.random() * W, y: Math.random() * H,
        r: Math.random() * 2 + 0.5,
        dx: (Math.random() - 0.5) * 0.4,
        dy: (Math.random() - 0.5) * 0.4,
        alpha: Math.random() * 0.6 + 0.2,
        color: Math.random() > 0.5 ? '96,165,250' : '167,139,250'
    });
}

function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color},${p.alpha})`;
        ctx.fill();
        p.x += p.dx; p.y += p.dy;
        if (p.x < 0 || p.x > W) p.dx *= -1;
        if (p.y < 0 || p.y > H) p.dy *= -1;
    });
    for (let i = 0; i < particles.length; i++) {
        for (let j = i+1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const d = Math.sqrt(dx*dx + dy*dy);
            if (d < 120) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.strokeStyle = `rgba(96,165,250,${0.12*(1-d/120)})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(draw);
}
draw();
</script>
""", unsafe_allow_html=True)

# ── BOTÓN CTA ──────────────────────────────────────────────────────────────────
st.markdown('<div class="cta-center">', unsafe_allow_html=True)
if st.button(" Entrar al Dashboard  →"):
    st.switch_page("pages/1_Dashboard.py")
st.markdown('</div>', unsafe_allow_html=True)

# ── STATS + SECCIONES ─────────────────────────────────────────────────────────
st.markdown("""
<div class="landing-wrap">
  <div class="stats-bar">
    <div class="stat-item"><div class="stat-number">~3K</div><div class="stat-label">Posts analizados</div></div>
    <div class="stat-item"><div class="stat-number">3</div><div class="stat-label">Comunidades de IA</div></div>
    <div class="stat-item"><div class="stat-number">2</div><div class="stat-label">Modelos NLP</div></div>
    <div class="stat-item"><div class="stat-number">3</div><div class="stat-label">Perfiles de usuario</div></div>
  </div>

  <div class="how-section">
    <div class="section-title">¿Cómo <span>funciona</span>?</div>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-number">01</div>
        <div class="step-icon">📡</div>
        <div class="step-title">Extracción de datos</div>
        <div class="step-desc">Se conecta a Reddit y extrae hasta 1000 títulos de posts de la comunidad seleccionada usando su API pública.</div>
      </div>
      <div class="step-card">
        <div class="step-number">02</div>
        <div class="step-icon">🧠</div>
        <div class="step-title">Análisis con IA</div>
        <div class="step-desc">Pipeline de dos niveles: VADER analiza todos los posts, RoBERTa profundiza en los más virales para mayor precisión.</div>
      </div>
      <div class="step-card">
        <div class="step-number">03</div>
        <div class="step-icon">👥</div>
        <div class="step-title">Segmentación</div>
        <div class="step-desc">K-Means + TF-IDF agrupa los posts en clusters temáticos y clasifica a los usuarios en 3 perfiles de innovación.</div>
      </div>
    </div>
  </div>

  <div class="tech-section">
    <div class="section-title">Tecnologías <span>utilizadas</span></div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-icon">⚡</div>
        <div class="tech-name">VADER</div>
        <div class="tech-desc">Análisis de sentimiento optimizado para redes sociales</div>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🤖</div>
        <div class="tech-name">RoBERTa</div>
        <div class="tech-desc">Modelo transformer fine-tuneado sobre 58M tweets</div>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🔵</div>
        <div class="tech-name">K-Means</div>
        <div class="tech-desc">Clustering no supervisado con vectorización TF-IDF</div>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🌊</div>
        <div class="tech-name">Streamlit</div>
        <div class="tech-desc">Framework de visualización interactiva en Python</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)