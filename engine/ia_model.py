import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Aseguramos recursos NLTK para la memoria técnica
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class InnoAnalyzer:
    def __init__(self, n_clusters=3):
        """Constructor del motor de Inteligencia de Negocio."""
        self.stop_words = list(stopwords.words('english')) + ['ai', 'intelligence', 'artificial']
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = TfidfVectorizer(
            max_features=500, # Aumentamos la dimensionalidad
            ngram_range=(1, 2), # Unigramas y Bigramas (más 'pro')
            stop_words=self.stop_words
        )
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)

    def _pipeline_nlp(self, text):
        """Pipeline avanzado de limpieza y normalización semántica."""
        # 1. Limpieza de ruido y normalización
        text = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
        # 2. Tokenización y Lematización (vuelve las palabras a su raíz)
        tokens = text.split()
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens if t not in self.stop_words]
        return " ".join(tokens)

    def process_data(self, df):
        """Ejecuta el ciclo completo de Machine Learning sobre los datos."""
        if df.empty: return df

        # Aplicamos el Pipeline avanzado
        df['titulo_limpio'] = df['titulo'].apply(self._pipeline_nlp)
        
        # Vectorización avanzada TF-IDF (Term Frequency - Inverse Document Frequency)
        tfidf_matrix = self.vectorizer.fit_transform(df['titulo_limpio'])
        
        # Ejecución del Algoritmo de Agrupamiento K-Means
        df['cluster_id'] = self.kmeans.fit_predict(tfidf_matrix)
        
        # Análisis de Polaridad de Sentimiento
        df['sentimiento_puntuacion'] = df['titulo'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
        
        # Clasificación Heurística de Perfiles de Innovación
        df['perfil_usuario'] = df['sentimiento_puntuacion'].apply(self._label_profile)
        
        return df

    def _label_profile(self, score):
        """Asignación de etiquetas basadas en análisis de sentimiento."""
        if score > 0.15: return "Tecnófilos (Innovación)"
        if score < -0.15: return "Preocupados (Ética/Riesgos)"
        return "Curiosos (Herramientas/Dudas)"