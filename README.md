# SentAI-Scan

> Escáner de sentimiento en comunidades de Reddit sobre Inteligencia Artificial.

[![Status](https://img.shields.io/badge/Status-Live-brightgreen)](https://sentai-scan.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-ff4b4b)](https://streamlit.io)

**Demo en producción:** https://sentai-scan.streamlit.app

---

## ¿Qué es SentAI-Scan?

SentAI-Scan analiza el sentimiento de posts en subreddits de IA (r/ArtificialIntelligence, r/MachineLearning, r/ChatGPT). Extrae los títulos más populares, los procesa con un pipeline de NLP y los clasifica en tres perfiles de usuario: **Tecnófilos**, **Curiosos** y **Preocupados**.

---

## Arquitectura del sistema

```
Reddit API → Pre-procesamiento NLP → TF-IDF + K-Means → VADER + RoBERTa → Dashboard
```

### Pipeline completo

**1. Extracción**
Scraping de la API pública de Reddit (`/hot.json`) con paginación automática hasta 1000 posts.

**2. Pre-procesamiento**
Limpieza con Regex, eliminación de stopwords y lematización con WordNetLemmatizer (NLTK).

**3. Clustering**
Vectorización TF-IDF con bigramas y segmentación K-Means en 3 clusters temáticos:
- Tecnófilos
- Curiosos
- Preocupados

**4. Análisis de sentimiento (2 niveles)**
- **VADER** — análisis rápido de todos los posts, optimizado para redes sociales
- **RoBERTa**  — análisis profundo de los top 200 posts por puntuación

Puntuación final: `60% RoBERTa + 40% VADER`

**5. Clasificación de perfiles**
Basada en la puntuación combinada de sentimiento.

---

## Dashboard — 6 secciones

1. **Termómetro de Sentimiento** — Gauge de polaridad global, KPIs e interpretación automática
2. **Posts Virales vs Sentimiento** — Top 15 posts coloreados por sentimiento
3. **Mapa de Controversia** — Scatter de engagement y radar de perfiles normalizado
4. **Vocabulario por Perfil** — WordCloud diferenciado por segmento de usuario
5. **Segmentación y Detalle** — Tabla de top posts y distribución de perfiles
6. **Exportar Datos** — Descarga en CSV del dataset completo, top 100 o resumen por perfil

---

## Estructura del proyecto

```
SentAI-Scan/
├── app.py                    # Landing page
├── navbar.py                 # Componente de navegación
├── style.css                 # Estilos del dashboard
├── requirements.txt
├── nltk.txt                  # Recursos NLTK para Streamlit Cloud
├── Dockerfile
├── core/
│   └── reddit_client.py      # Extracción de datos + fallback demo
├── engine/
│   └── ia_model.py           # Pipeline NLP: VADER + RoBERTa + K-Means
├── database/
│   ├── demo_ArtificialInteligence.csv
│   ├── demo_MachineLearning.csv
│   └── demo_ChatGPT.csv
└── pages/
    ├── 1_Dashboard.py
    └── 2_Sobre_el_TFG.py
```

---

## Instalación local

```bash
git clone https://github.com/fran2003pan-star/SentAI-Scan
cd SentAI-Scan

python -m venv tfg_env
tfg_env\Scripts\activate        # Windows
source tfg_env/bin/activate     # Mac/Linux

pip install -r requirements.txt
streamlit run app.py
```

---

## Nota sobre el modo demo

Reddit restringió el acceso a su API oficial en 2023. La versión desplegada opera con un dataset de ~3.000 posts reales recopilados previamente. Para activar datos en tiempo real bastaría con sustituir `fetch_reddit_data()` en `core/reddit_client.py` por una llamada autenticada con **PRAW**, añadiendo `client_id`, `client_secret` y `user_agent`.

---

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3.10 | Lenguaje principal |
| Streamlit | Interfaz web |
| VADER (NLTK) | Sentimiento nivel 1 |
| RoBERTa (HuggingFace) | Sentimiento nivel 2 |
| scikit-learn | TF-IDF + K-Means |
| Plotly | Visualizaciones |
| WordCloud | Nube de palabras |
| SQLite | Persistencia local |
| Streamlit Cloud | Despliegue |

---

*Trabajo de Fin de Grado — Grado en Gestión de Información y Contenidos Digitales*  
*Universidad de Murcia · 2026 · Franco Panero · Tutor: Juan José López Jiménez*
