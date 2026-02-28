# 🛰️ SentAI Scan: AI Intelligence System

![Status](https://img.shields.io/badge/Status-Live-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED)

**SentAI Scan** es una plataforma avanzada de **Inteligencia de Negocio y Análisis de Tendencias** diseñada para monitorizar la percepción pública sobre la Inteligencia Artificial en tiempo real. Este sistema extrae datos masivos de comunidades especializadas, aplica modelos de Machine Learning y genera un dashboard interactivo de alta fidelidad.

## 🚀 Acceso al Sistema
Cualquier usuario puede acceder a la instancia en producción a través del siguiente enlace:
👉 https://sentai-scan.streamlit.app/

---

## 🧠 Arquitectura de Inteligencia Artificial

El núcleo del sistema utiliza un pipeline de **Procesamiento de Lenguaje Natural (NLP)** y aprendizaje no supervisado:

1.  **Ingesta de Datos:** Extracción dinámica enfocada en subreddits de tecnología (AI, Machine Learning, ChatGPT).
2.  **Pre-procesamiento:** Implementación de limpieza mediante Regex, eliminación de *stopwords* y normalización semántica.
3.  **Vectorización TF-IDF:** Transformación de texto a vectores numéricos considerando la relevancia estadística de los términos.
4.  **Clustering K-Means:** Segmentación automática de la audiencia en tres perfiles psicográficos: **Tecnófilos**, **Curiosos** y **Preocupados**.
5.  **Sentiment Analysis:** Cálculo de polaridad mediante la librería `TextBlob` para determinar el "termómetro" emocional de la conversación.

## 📊 Dashboard de 4 Niveles

El sistema presenta los resultados siguiendo una jerarquía de análisis de datos profesional:
* **Nivel 1 (Termómetro):** KPIs clave de sentimiento global y volumen de posts.
* **Nivel 2 (Segmentación):** Visualización  de clusters mediante gráficos de dispersión de alta dimensionalidad.
* **Nivel 3 (Detalle Semántico):** Análisis comparativo de perfiles y tabla de impacto por interacciones.
* **Nivel 4 (Persistencia):** Histórico de análisis almacenado en una base de datos **SQLite**.

## 🐳 Despliegue e Infraestructura

Este proyecto ha sido diseñado bajo principios de **Software Engineering**:
* **Dockerización:** Incluye un `Dockerfile` que encapsula todas las dependencias y recursos de NLTK, garantizando la reproducibilidad del entorno en cualquier host.
* **CI/CD:** Despliegue continuo integrado con GitHub y Streamlit Cloud para actualizaciones automáticas.
* **UI/UX:** Interfaz personalizada mediante **CSS externo**, utilizando técnicas de *Glassmorphism* y diseño adaptativo para dispositivos móviles.

---
*Este proyecto forma parte de mi Trabajo de Fin de Grado (TFG) en Gestion de la Informacion y los Contenidos Digitales (UMU)*
