🛰️ SentAI-Scan
Mostrar imagen
Mostrar imagen
Mostrar imagen
Mostrar imagen
SentAI-Scan es un sistema de análisis de sentimiento aplicado a comunidades de inteligencia artificial en Reddit. El proyecto combina técnicas de Procesamiento del Lenguaje Natural (NLP) con algoritmos de clustering no supervisado para detectar tendencias, emociones y perfiles de usuario en posts sobre IA.
🔗 Demo en producción: https://sentai-scan.streamlit.app

🧠 Arquitectura del Sistema
El núcleo del sistema implementa un pipeline de NLP y aprendizaje no supervisado:

Extracción de datos — Scraping de la API pública de Reddit (/hot.json) para obtener títulos, puntuaciones y comentarios de los subreddits seleccionados.
Pre-procesamiento NLP — Limpieza con Regex, eliminación de stopwords y lematización con WordNetLemmatizer (NLTK).
Vectorización TF-IDF — Transformación de texto a vectores numéricos con bigramas (ngram_range=(1,2), max_features=500).
Clustering K-Means — Segmentación automática en 3 clusters temáticos: IA Generativa & LLMs, Automatización & Trabajo y Ética & Regulación.
Análisis de Sentimiento (2 niveles):

VADER — Análisis rápido de todos los posts, optimizado para lenguaje de redes sociales.
RoBERTa (cardiffnlp/twitter-roberta-base-sentiment) — Análisis profundo sobre los top 200 posts por puntuación. Puntuación final combinada: 60% RoBERTa + 40% VADER.


Clasificación de perfiles — Basada en la puntuación combinada de sentimiento: Tecnófilos, Curiosos y Preocupados.


📊 Dashboard — 6 Secciones
#SecciónDescripción1🌡️ Termómetro de SentimientoGauge de polaridad global + interpretación automática + KPIs2🔥 Posts Virales vs SentimientoTop 15 posts coloreados por sentimiento3🗺️ Mapa de ControversiaScatter de engagement + Radar de perfiles normalizado4💬 Vocabulario por PerfilWordCloud diferenciado por segmento de usuario5📊 Segmentación y DetalleTabla top posts + distribución de perfiles6📥 Exportar DatosDescarga en CSV: dataset completo, top 100 y resumen por perfil

⚠️ Nota técnica sobre el modo demo
Reddit restringió el acceso gratuito a su API oficial en 2023, lo que imposibilitó obtener credenciales para este proyecto. La versión desplegada opera con un dataset de referencia de ~3.000 posts reales previamente recopilados mediante la API pública.
La adaptación a la API oficial sería sencilla: bastaría con sustituir fetch_reddit_data() en core/reddit_client.py por una llamada autenticada con PRAW (librería oficial de Reddit para Python), añadiendo client_id, client_secret y user_agent. Con ese cambio el sistema funcionaría en tiempo real para cualquier usuario.

🗂️ Estructura del Proyecto
SentAI-Scan/
├── app.py                  # Landing page animada
├── navbar.py               # Componente de navegación compartido
├── style.css               # Estilos globales del dashboard
├── requirements.txt        # Dependencias del proyecto
├── nltk.txt                # Recursos NLTK para Streamlit Cloud
├── Dockerfile              # Despliegue alternativo con Docker
├── core/
│   └── reddit_client.py    # Extracción de datos de Reddit + fallback demo
├── engine/
│   └── ia_model.py         # Pipeline NLP: VADER + RoBERTa + K-Means
├── database/
│   ├── radar_innovacion_ia.db      # Base de datos SQLite local
│   ├── demo_ArtificialInteligence.csv
│   ├── demo_MachineLearning.csv
│   └── demo_ChatGPT.csv
└── pages/
    ├── 1_Dashboard.py      # Dashboard principal con 6 secciones
    └── 2_Sobre_el_TFG.py   # Presentación del autor y del proyecto

⚙️ Instalación y Ejecución Local
bash# 1. Clonar el repositorio
git clone https://github.com/fran2003pan-star/SentAI-Scan
cd SentAI-Scan

# 2. Crear y activar entorno virtual
python -m venv tfg_env
tfg_env\Scripts\activate      # Windows
source tfg_env/bin/activate   # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py

🛠️ Tecnologías Utilizadas
TecnologíaUsoPython 3.10Lenguaje principalStreamlitFramework de visualización e interfaz webVADER (NLTK)Análisis de sentimiento nivel 1RoBERTa (HuggingFace)Análisis de sentimiento nivel 2scikit-learnTF-IDF + K-Means clusteringPlotlyVisualizaciones interactivasWordCloudNube de palabras por perfilSQLitePersistencia local de análisisDockerDespliegue alternativoGitHub + Streamlit CloudCI/CD y hosting

🚀 Despliegue
El proyecto está desplegado en Streamlit Cloud conectado directamente a este repositorio. Cualquier git push a la rama main actualiza automáticamente la aplicación en producción.
Se incluye también un Dockerfile para despliegue alternativo en servidor propio.

Trabajo de Fin de Grado — Grado en Gestión de Información y Contenidos Digitales
Facultad de Comunicación y Documentación — Universidad de Murcia · 2026
Autor: Franco Panero · Tutor: Juan José López Jiménez
