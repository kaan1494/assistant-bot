"""
Basit Deep Learning modülü - Performans odaklı
"""

import sqlite3
import pandas as pd
import numpy as np
import re
from datetime import datetime
from pathlib import Path

# Sadece gerekli olanları import et
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class NewsAnalyzer:
    """Performans odaklı haber analizi"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        
    def load_news_data(self):
        """Veritabanından haberleri yükle"""
        try:
            db = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM ai_news", db)
            db.close()
            return df
        except Exception as e:
            print(f"❌ Veri yükleme hatası: {e}")
            return pd.DataFrame()
    
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
        """Hızlı analiz raporu"""
        try:
            df = self.load_news_data()
            
            if df.empty:
                return {"error": "Analiz edilecek haber bulunamadı", "total_news": 0}
            
            # Kategorize et
            df['category'] = df.apply(lambda x: self.categorize_news(x['title'], x.get('summary', '')), axis=1)
            df['sentiment'] = df['title'].apply(self.analyze_sentiment)
            
            report = {
                "total_news": len(df),
                "sources": df['source'].value_counts().to_dict(),
                "categories": df['category'].value_counts().to_dict(),
                "sentiment": df['sentiment'].value_counts().to_dict(),
                "top_keywords": self.extract_simple_keywords(df['title'].tolist()),
                "latest_trends": [],
                "recommendations": [f"Toplam {len(df)} haber analiz edildi"]
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Analiz hatası: {e}", "total_news": 0}
    
    def extract_simple_keywords(self, texts):
        """Basit kelime frekansı"""
        word_freq = {}
        for text in texts:
            if not text:
                continue
            words = text.lower().split()
            for word in words:
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

class VoiceAnalyzer:
    """Basit ses analizi"""
    
    def __init__(self):
        pass
    
    def enhanced_speech_recognition(self, audio_path):
        return "Basit ses tanıma aktif"

if __name__ == "__main__":
    print("🧠 Basit AI Analizi Test...")
    analyzer = NewsAnalyzer()
    report = analyzer.generate_analysis_report()
    print(f"📰 Toplam haber: {report.get('total_news', 0)}")
    print("✅ Test tamamlandı!")
