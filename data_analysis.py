import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

def analyze_current_data():
    """Mevcut verileri analiz et ve Deep Learning için uygun hale getir"""
    
    # Veritabanından verileri çek
    db = sqlite3.connect('data/assistant.db')
    
    # Haberleri analiz et
    news_df = pd.read_sql_query("SELECT * FROM ai_news", db)
    print("📰 Haber Verileri Analizi:")
    print(f"  - Toplam haber: {len(news_df)}")
    print(f"  - Kaynak dağılımı:")
    source_counts = news_df['source'].value_counts()
    for source, count in source_counts.items():
        print(f"    • {source}: {count}")
    
    # Notları analiz et
    notes_df = pd.read_sql_query("SELECT * FROM notes", db)
    print(f"\n📝 Not Verileri:")
    print(f"  - Toplam not: {len(notes_df)}")
    
    # Hatırlatmaları analiz et
    reminders_df = pd.read_sql_query("SELECT * FROM reminders", db)
    print(f"\n⏰ Hatırlatma Verileri:")
    print(f"  - Toplam hatırlatma: {len(reminders_df)}")
    
    db.close()
    
    # Deep Learning için veri önerileri
    print("\n🤖 Deep Learning İçin Öneriler:")
    print("1. 📊 Haber Sınıflandırma (NLP)")
    print("2. 🎯 Konu Modelleme (Topic Modeling)")
    print("3. 📈 Trend Analizi (Time Series)")
    print("4. 🔮 Haber Önerileri (Recommendation)")
    print("5. 🎤 Gelişmiş Ses Analizi (Speech-to-Text)")
    print("6. 💬 Doğal Dil İşleme (NLU/NLG)")
    
    return news_df, notes_df, reminders_df

if __name__ == "__main__":
    analyze_current_data()
