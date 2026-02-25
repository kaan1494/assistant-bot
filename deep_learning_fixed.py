"""
Basit Deep Learning entegrasyonu - Hata düzeltmeleri
"""

import sqlite3
import pandas as pd
import numpy as np
import re
import json
from datetime import datetime
from pathlib import Path

# Temel NLP kütüphaneleri
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn mevcut değil. Temel analiz kullanılacak.")

# Deep Learning (opsiyonel)
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

class NewsAnalyzer:
    """Basit ve çalışan haber analizi sınıfı"""
    
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
    
    def preprocess_text(self, text):
        """Basit metin temizleme"""
        if not text:
            return ""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords_simple(self, texts, max_words=20):
        """Basit kelime frekansı analizi"""
        if not texts:
            return []
        
        word_freq = {}
        for text in texts:
            if not text:
                continue
            processed = self.preprocess_text(text)
            words = processed.split()
            for word in words:
                if len(word) > 3:  # Kısa kelimeler hariç
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # En sık geçen kelimeleri döndür
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_words]
    
    def extract_keywords_advanced(self, texts, max_words=20):
        """TF-IDF ile gelişmiş analiz"""
        if not SKLEARN_AVAILABLE or not texts:
            return self.extract_keywords_simple(texts, max_words)
        
        try:
            processed_texts = [self.preprocess_text(text) for text in texts if text]
            if not processed_texts:
                return []
            
            vectorizer = TfidfVectorizer(
                max_features=max_words,
                ngram_range=(1, 2),
                stop_words=None
            )
            
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.sum(axis=0).A1
            
            keyword_scores = list(zip(feature_names, scores))
            return sorted(keyword_scores, key=lambda x: x[1], reverse=True)[:max_words]
        except Exception as e:
            print(f"⚠️ TF-IDF hatası, basit analiz kullanılıyor: {e}")
            return self.extract_keywords_simple(texts, max_words)
    
    def categorize_news(self, title, summary=""):
        """Haberi kategorize et"""
        text = f"{title} {summary}".lower()
        
        categories = {
            "teknoloji": ["teknoloji", "ai", "yapay zeka", "algoritma", "model", "chip", "gpu", "donanım"],
            "iş_dünyası": ["şirket", "yatırım", "pazar", "startup", "girişim", "büyüme", "satış"],
            "araştırma": ["araştırma", "akademi", "üniversite", "makale", "çalışma", "bilim"],
            "ürün": ["ürün", "uygulama", "platform", "sistem", "araç", "bot", "servis"],
            "politika": ["politika", "düzenleme", "yasa", "devlet", "hükümet", "kanun"]
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
        if not text:
            return "nötr"
        
        positive_words = ["başarılı", "gelişmiş", "yeni", "ileri", "güçlü", "hızlı", "etkili", "iyi", "mükemmel"]
        negative_words = ["sorun", "problem", "hata", "risk", "tehlike", "yavaş", "zayıf", "kötü", "başarısız"]
        
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
        try:
            df = self.load_news_data()
            
            if df.empty:
                return {
                    "error": "Analiz edilecek haber bulunamadı",
                    "total_news": 0,
                    "sources": {},
                    "categories": {},
                    "sentiment": {},
                    "top_keywords": [],
                    "latest_trends": [],
                    "recommendations": ["Henüz haber verisi yok"]
                }
            
            # Kategorilere ayır
            df['category'] = df.apply(lambda x: self.categorize_news(x['title'], x.get('summary', '')), axis=1)
            df['sentiment'] = df['title'].apply(self.analyze_sentiment)
            
            # Anahtar kelimeleri çıkar
            if SKLEARN_AVAILABLE:
                keywords = self.extract_keywords_advanced(df['title'].tolist())
            else:
                keywords = self.extract_keywords_simple(df['title'].tolist())
            
            # İstatistikler
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
            
        except Exception as e:
            print(f"❌ Analiz hatası: {e}")
            return {
                "error": f"Analiz hatası: {e}",
                "total_news": 0,
                "sources": {},
                "categories": {},
                "sentiment": {},
                "top_keywords": [],
                "latest_trends": [],
                "recommendations": []
            }
    
    def identify_trends(self, df):
        """Trend analizi"""
        try:
            recent_titles = df['title'].str.lower()
            trend_words = {}
            
            for title in recent_titles:
                if not title:
                    continue
                words = title.split()
                for word in words:
                    if len(word) > 3:
                        trend_words[word] = trend_words.get(word, 0) + 1
            
            trends = sorted(trend_words.items(), key=lambda x: x[1], reverse=True)[:5]
            return trends
        except Exception as e:
            print(f"❌ Trend analizi hatası: {e}")
            return []
    
    def generate_recommendations(self, df):
        """Kişiselleştirilmiş öneriler"""
        try:
            recommendations = []
            
            if not df.empty:
                top_category = df['category'].mode().iloc[0] if len(df['category'].mode()) > 0 else "teknoloji"
                recommendations.append(f"En popüler kategori: {top_category}")
                
                top_source = df['source'].mode().iloc[0] if len(df['source'].mode()) > 0 else ""
                if top_source:
                    recommendations.append(f"En aktif kaynak: {top_source}")
                
                positive_ratio = (df['sentiment'] == 'pozitif').sum() / len(df) * 100
                recommendations.append(f"Pozitif haber oranı: %{positive_ratio:.1f}")
            
            return recommendations
        except Exception as e:
            print(f"❌ Öneri oluşturma hatası: {e}")
            return ["Öneri oluşturulamadı"]

# Test fonksiyonu
def test_analyzer():
    """Analizcıyı test et"""
    print("🧪 Deep Learning Analiz Testi...")
    
    analyzer = NewsAnalyzer()
    report = analyzer.generate_analysis_report()
    
    print(f"📰 Toplam haber: {report.get('total_news', 0)}")
    print(f"📂 Kategoriler: {report.get('categories', {})}")
    print(f"💭 Duygu dağılımı: {report.get('sentiment', {})}")
    
    keywords = report.get('top_keywords', [])
    if keywords:
        top_words = [k[0] for k in keywords[:5]]
        print(f"🔥 Trend kelimeler: {top_words}")
    
    if report.get('error'):
        print(f"⚠️ Hata: {report['error']}")
    
    # Kurulum durumu
    print(f"\n🛠️ Kurulum Durumu:")
    print(f"  • Scikit-learn: {'✅' if SKLEARN_AVAILABLE else '❌'}")
    print(f"  • PyTorch: {'✅' if TORCH_AVAILABLE else '❌'}")
    
    return report

if __name__ == "__main__":
    test_analyzer()
