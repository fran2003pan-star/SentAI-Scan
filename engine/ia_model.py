import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# Descarga de recursos NLTK necesarios
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('vader_lexicon', quiet=True)

# Intentamos cargar el modelo Transformers (opcional pero recomendado)
try:
    from transformers import pipeline as hf_pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


# ─────────────────────────────────────────────
#  CONSTANTES DE CONFIGURACIÓN
# ─────────────────────────────────────────────
# Top N posts (por puntuación) a los que se les aplica RoBERTa (más costoso)
ROBERTA_TOP_N = 200
# Nombre del modelo HuggingFace a usar
ROBERTA_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"


class InnoAnalyzer:
    """
    Motor de análisis de sentimiento e innovación de dos niveles:

    - Nivel 1 (todos los posts): VADER — rápido, optimizado para redes sociales.
    - Nivel 2 (top N posts):     RoBERTa — modelo transformer fine-tuneado sobre
                                  tweets, con mayor precisión en lenguaje informal
                                  y terminología tecnológica.
    """

    def __init__(self, n_clusters: int = 3):
        # ── Stopwords y lematizador ──────────────────────────────────────────
        self.stop_words = (
            list(stopwords.words('english'))
            + ['ai', 'intelligence', 'artificial', 'like', 'get', 'use']
        )
        self.lemmatizer = WordNetLemmatizer()

        # ── TF-IDF + K-Means ────────────────────────────────────────────────
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words=self.stop_words
        )
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)

        # ── Nivel 1: VADER ───────────────────────────────────────────────────
        self.vader = SentimentIntensityAnalyzer()

        # ── Nivel 2: RoBERTa (opcional) ──────────────────────────────────────
        self.roberta = None
        if TRANSFORMERS_AVAILABLE:
            try:
                self.roberta = hf_pipeline(
                    "sentiment-analysis",
                    model=ROBERTA_MODEL,
                    tokenizer=ROBERTA_MODEL,
                    truncation=True,
                    max_length=128
                )
                print("✅ Modelo RoBERTa cargado correctamente.")
            except Exception as e:
                print(f"⚠️  RoBERTa no disponible, usando solo VADER. ({e})")

    # ─────────────────────────────────────────────────────────────────────────
    #  PIPELINE NLP
    # ─────────────────────────────────────────────────────────────────────────
    def _pipeline_nlp(self, text: str) -> str:
        """Limpieza y normalización semántica del texto."""
        text = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
        tokens = text.split()
        tokens = [
            self.lemmatizer.lemmatize(t)
            for t in tokens
            if t not in self.stop_words and len(t) > 2
        ]
        return " ".join(tokens)

    # ─────────────────────────────────────────────────────────────────────────
    #  ANÁLISIS DE SENTIMIENTO - NIVEL 1: VADER
    # ─────────────────────────────────────────────────────────────────────────
    def _vader_score(self, text: str) -> float:
        """
        Devuelve el compound score de VADER [-1, 1].
        VADER está optimizado para texto de redes sociales:
        entiende mayúsculas, puntuación expresiva y negaciones.
        """
        return self.vader.polarity_scores(str(text))['compound']

    # ─────────────────────────────────────────────────────────────────────────
    #  ANÁLISIS DE SENTIMIENTO - NIVEL 2: RoBERTa
    # ─────────────────────────────────────────────────────────────────────────
    def _roberta_score(self, text: str) -> float | None:
        """
        Devuelve una puntuación normalizada [-1, 1] desde RoBERTa.
        Etiquetas del modelo: LABEL_0=negativo, LABEL_1=neutro, LABEL_2=positivo.
        Retorna None si el modelo no está disponible.
        """
        if self.roberta is None:
            return None
        try:
            result = self.roberta(str(text)[:512])[0]
            label  = result['label']
            score  = result['score']
            if label == 'LABEL_2':   return score        #  positivo → [0, 1]
            if label == 'LABEL_0':   return -score       #  negativo → [-1, 0]
            return 0.0                                   #  neutro
        except Exception:
            return None

    # ─────────────────────────────────────────────────────────────────────────
    #  PROCESO COMPLETO
    # ─────────────────────────────────────────────────────────────────────────
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta el pipeline completo sobre el DataFrame de posts:
          1. Limpieza NLP
          2. Vectorización TF-IDF + Clustering K-Means
          3. VADER para todos los posts
          4. RoBERTa para los top ROBERTA_TOP_N posts (por puntuación)
          5. Puntuación final combinada y perfiles de usuario
        """
        if df.empty:
            return df

        df = df.copy()

        # ── 1. Limpieza ──────────────────────────────────────────────────────
        df['titulo_limpio'] = df['titulo'].apply(self._pipeline_nlp)

        # ── 2. TF-IDF + K-Means ─────────────────────────────────────────────
        tfidf_matrix = self.vectorizer.fit_transform(df['titulo_limpio'])
        df['cluster_id'] = self.kmeans.fit_predict(tfidf_matrix)
        df['tema_cluster'] = df['cluster_id'].map(self._label_cluster)

        # ── 3. VADER (todos los posts) ───────────────────────────────────────
        df['sentimiento_vader'] = df['titulo'].apply(self._vader_score)

        # ── 4. RoBERTa (solo top N por puntuación) ───────────────────────────
        df['sentimiento_roberta'] = None

        if self.roberta is not None:
            top_idx = (
                df['puntuacion']
                .nlargest(min(ROBERTA_TOP_N, len(df)))
                .index
            )
            df.loc[top_idx, 'sentimiento_roberta'] = (
                df.loc[top_idx, 'titulo'].apply(self._roberta_score)
            )

        # ── 5. Puntuación final combinada ────────────────────────────────────
        # • Si RoBERTa analizó el post → promedio ponderado (60 % RoBERTa, 40 % VADER)
        # • Si no → solo VADER
        def _combine(row):
            if pd.notna(row['sentimiento_roberta']):
                return 0.6 * row['sentimiento_roberta'] + 0.4 * row['sentimiento_vader']
            return row['sentimiento_vader']

        df['sentimiento_puntuacion'] = df.apply(_combine, axis=1)

        # ── 6. Fuente del análisis (útil para transparencia en dashboard) ────
        df['fuente_sentimiento'] = df['sentimiento_roberta'].apply(
            lambda x: 'RoBERTa+VADER' if pd.notna(x) else 'VADER'
        )

        # ── 7. Perfiles de usuario ───────────────────────────────────────────
        df['perfil_usuario'] = df['sentimiento_puntuacion'].apply(self._label_profile)

        return df

    # ─────────────────────────────────────────────────────────────────────────
    #  ETIQUETADO
    # ─────────────────────────────────────────────────────────────────────────
    def _label_profile(self, score: float) -> str:
        """Clasifica el perfil según la puntuación de sentimiento combinada."""
        if score > 0.15:   return "Tecnófilos (Innovación)"
        if score < -0.15:  return "Preocupados (Ética/Riesgos)"
        return "Curiosos (Herramientas/Dudas)"

    def _label_cluster(self, cluster_id: int) -> str:
        """
        Etiquetas temáticas heurísticas para los 3 clusters.
        En una versión avanzada, estas se podrían inferir automáticamente
        inspeccionando las top keywords de cada cluster con get_feature_names_out().
        """
        labels = {
            0: "IA Generativa & LLMs",
            1: "Automatización & Trabajo",
            2: "Ética & Regulación"
        }
        return labels.get(cluster_id, f"Cluster {cluster_id}")