"""
Deep Learning modülü - Haber analizi ve NLP işlemleri
"""

import sqlite3
import pandas as pd
import numpy as np
import re
import pickle
from datetime import datetime
from pathlib import Path

# Deep Learning kütüphaneleri (kurulum sonrası)
try:
    import torch
    import torch.nn as nn
    from transformers import AutoTokenizer, AutoModel, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn kurulu değil. Temel analiz kullanılacak.")

DEEP_LEARNING_AVAILABLE = TRANSFORMERS_AVAILABLE and SKLEARN_AVAILABLE

class NewsAnalyzer:
    """Haber analizi ve sınıflandırma sınıfı"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.models_dir = Path("data/models")
        self.models_dir.mkdir(exist_ok=True)
        
    def load_news_data(self):
        """Veritabanından haberleri yükle"""
        db = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM ai_news", db)
        db.close()
        return df
    
    def preprocess_text(self, text):
        """Metin ön işleme"""
        if not text:
            return ""
        
        # Türkçe karakterleri koru, gereksiz karakterleri temizle
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords(self, texts, max_features=50):
        """Metinlerden anahtar kelimeleri çıkar - Basit versiyon"""
        if not texts:
            return []
        
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Basit kelime frekansı analizi
        word_freq = {}
        for text in processed_texts:
            words = text.split()
            for word in words:
                if len(word) > 3:  # Kısa kelimeler hariç
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # En sık geçen kelimeleri döndür
        keyword_scores = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return keyword_scores[:20]
    
    def categorize_news(self, title, summary=""):
        """Haberi kategorize et"""
        text = f"{title} {summary}".lower()
        
        categories = {
            "teknoloji": ["teknoloji", "ai", "yapay zeka", "algoritma", "model", "chip", "gpu"],
            "iş_dünyası": ["şirket", "yatırım", "pazar", "startup", "girişim", "büyüme"],
            "araştırma": ["araştırma", "akademi", "üniversite", "makale", "çalışma"],
            "ürün": ["ürün", "uygulama", "platform", "sistem", "araç", "bot"],
            "politika": ["politika", "düzenleme", "yasa", "devlet", "hükümet"]
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # En yüksek skorlu kategoriyi döndür
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "genel"
    
    def analyze_sentiment(self, text):
        """Basit duygu analizi"""
        positive_words = ["başarılı", "gelişmiş", "yeni", "ileri", "güçlü", "hızlı", "etkili"]
        negative_words = ["sorun", "problem", "hata", "risk", "tehlike", "yavaş", "zayıf"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "pozitif"
        elif negative_count > positive_count:
            return "negatif"
        return "nötr"
    
    def generate_analysis_report(self):
        """Kapsamlı analiz raporu oluştur"""
        df = self.load_news_data()
        
        if df.empty:
            return {"error": "Analiz edilecek haber bulunamadı"}
        
        # Kategorilere ayır
        df['category'] = df.apply(lambda x: self.categorize_news(x['title'], x.get('summary', '')), axis=1)
        df['sentiment'] = df['title'].apply(self.analyze_sentiment)
        
        # Anahtar kelimeleri çıkar
        keywords = self.extract_keywords(df['title'].tolist())
        
        # Kaynak analizi
        source_stats = df['source'].value_counts().to_dict()
        category_stats = df['category'].value_counts().to_dict()
        sentiment_stats = df['sentiment'].value_counts().to_dict()
        
        report = {
            "total_news": len(df),
            "sources": source_stats,
            "categories": category_stats,
            "sentiment": sentiment_stats,
            "top_keywords": keywords[:10],
            "latest_trends": self.identify_trends(df),
            "recommendations": self.generate_recommendations(df)
        }
        
        return report
    
    def identify_trends(self, df):
        """Trend analizi"""
        # Son haberlerdeki en sık geçen kelimeler
        recent_titles = df['title'].str.lower()
        trend_words = {}
        
        for title in recent_titles:
            words = title.split()
            for word in words:
                if len(word) > 3:  # Kısa kelimeler hariç
                    trend_words[word] = trend_words.get(word, 0) + 1
        
        # En popüler 5 trend
        trends = sorted(trend_words.items(), key=lambda x: x[1], reverse=True)[:5]
        return trends
    
    def generate_recommendations(self, df):
        """Kişiselleştirilmiş haber önerileri"""
        recommendations = []
        
        # Kategori bazlı öneriler
        top_category = df['category'].mode().iloc[0] if not df.empty else "teknoloji"
        recommendations.append(f"En popüler kategori: {top_category}")
        
        # Kaynak önerileri
        top_source = df['source'].mode().iloc[0] if not df.empty else ""
        if top_source:
            recommendations.append(f"En aktif kaynak: {top_source}")
        
        return recommendations

class VoiceAnalyzer:
    """Ses analizi ve konuşma tanıma geliştirmeleri"""
    
    def __init__(self):
        self.models_dir = Path("data/models/voice")
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def enhanced_speech_recognition(self, audio_path):
        """Gelişmiş konuşma tanıma"""
        # Mevcut speech_recognition kütüphanesini kullan
        # Gelecekte Whisper veya diğer modeller eklenebilir
        return "Gelişmiş ses tanıma - henüz implement edilmedi"
    
    def voice_emotion_detection(self, audio_path):
        """Sesten duygu tanıma"""
        # Ses tonundan duygu analizi
        return "nötr"  # Placeholder

def install_deep_learning_packages():
    """Deep Learning paketlerini kur"""
    packages = [
        "torch",
        "transformers", 
        "scikit-learn",
        "nltk",
        "spacy"
    ]
    
    print("🤖 Deep Learning paketleri kuruluyor...")
    for package in packages:
        print(f"  📦 {package} kuruluyor...")
    
    return """
    Kurulum komutları:
    pip install torch torchvision torchaudio
    pip install transformers
    pip install scikit-learn
    pip install nltk
    pip install spacy
    python -m spacy download tr_core_news_sm
    """

if __name__ == "__main__":
    print("🧠 Deep Learning Analizi Başlatılıyor...")
    
    analyzer = NewsAnalyzer()
    report = analyzer.generate_analysis_report()
    
    print("\n📊 Analiz Raporu:")
    print(f"📰 Toplam haber: {report['total_news']}")
    print(f"📂 Kategoriler: {report['categories']}")
    print(f"💭 Duygu dağılımı: {report['sentiment']}")
    print(f"🔥 Trend kelimeler: {[k[0] for k in report['top_keywords'][:5]]}")
    
    if not DEEP_LEARNING_AVAILABLE:
        print(f"\n{install_deep_learning_packages()}")
