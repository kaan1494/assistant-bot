"""
AI özelliklerini Telegram bot'a entegre eden modül
"""

try:
    from deep_learning_lite import NewsAnalyzer, VoiceAnalyzer
except ImportError:
    try:
        from deep_learning import NewsAnalyzer, VoiceAnalyzer
    except ImportError:
        print("⚠️ Deep learning modülleri yüklenemedi, basit analiz kullanılacak")
        
        class NewsAnalyzer:
            def __init__(self, db_path="data/assistant.db"):
                self.db_path = db_path
            def generate_analysis_report(self):
                return {"total_news": 0, "error": "AI modülleri yüklenemedi"}
        
        class VoiceAnalyzer:
            def __init__(self):
                pass
import json
from pathlib import Path

class AIAssistant:
    """AI asistan özellikleri"""
    
    def __init__(self):
        self.news_analyzer = NewsAnalyzer()
        self.voice_analyzer = VoiceAnalyzer()
        
    async def analyze_news_command(self, update, context):
        """📊 /analiz komutu - Haber analizi"""
        try:
            await update.message.reply_text("🧠 Haberler analiz ediliyor...")
            
            report = self.news_analyzer.generate_analysis_report()
            
            # Güzel formatlama
            response = f"""
📊 **Haber Analiz Raporu**

📰 **Toplam Haber:** {report['total_news']}

📂 **Kategoriler:**
{self._format_dict(report['categories'])}

💭 **Duygu Analizi:**
{self._format_dict(report['sentiment'])}

🔥 **Trend Kelimeler:**
{', '.join([k[0] for k in report['top_keywords'][:5]])}

📈 **Son Trendler:**
{', '.join([t[0] for t in report['latest_trends']])}

💡 **Öneriler:**
{chr(10).join(['• ' + rec for rec in report['recommendations']])}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Analiz hatası: {e}")
    
    async def smart_news_summary(self, update, context):
        """🤖 /özet komutu - Akıllı haber özeti"""
        try:
            await update.message.reply_text("🤖 Akıllı özet hazırlanıyor...")
            
            # Son haberleri al
            news_df = self.news_analyzer.load_news_data()
            
            if news_df.empty:
                await update.message.reply_text("📰 Henüz analiz edilecek haber yok.")
                return
            
            # Son 5 haberi kategorize et
            recent_news = news_df.tail(5)
            summary_text = "🤖 **Akıllı Haber Özeti**\n\n"
            
            for _, news in recent_news.iterrows():
                category = self.news_analyzer.categorize_news(news['title'])
                sentiment = self.news_analyzer.analyze_sentiment(news['title'])
                
                emoji = self._get_category_emoji(category)
                mood_emoji = self._get_sentiment_emoji(sentiment)
                
                summary_text += f"{emoji} **[{news['source']}]** {news['title'][:60]}...\n"
                summary_text += f"   📂 {category} {mood_emoji} {sentiment}\n\n"
            
            await update.message.reply_text(summary_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Özet hatası: {e}")
    
    async def trend_analysis(self, update, context):
        """📈 /trend komutu - Trend analizi"""
        try:
            await update.message.reply_text("📈 Trend analizi yapılıyor...")
            
            report = self.news_analyzer.generate_analysis_report()
            trends = report['latest_trends']
            
            if not trends:
                await update.message.reply_text("📈 Henüz trend verisi yok.")
                return
            
            trend_text = "📈 **Güncel Trendler**\n\n"
            
            for i, (word, count) in enumerate(trends, 1):
                bar = "▓" * min(count, 10)  # Görsel bar
                trend_text += f"{i}. **{word}** ({count}x) {bar}\n"
            
            await update.message.reply_text(trend_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Trend analizi hatası: {e}")
    
    async def ai_help(self, update, context):
        """🤖 /ai komutu - AI özellikleri yardımı"""
        help_text = """
🤖 **AI Asistan Özellikleri**

📊 **/analiz** - Haber analiz raporu
🤖 **/özet** - Akıllı haber özeti  
📈 **/trend** - Trend analizi
🎯 **/kategori** - Kategori dağılımı
💭 **/duygu** - Duygu analizi
🔮 **/tahmin** - Gelecek trendleri (yakında)

🎤 **Sesli AI:**
• Gelişmiş ses tanıma
• Duygu analizi
• Akıllı yanıtlar

📈 **Özellikler:**
• Real-time analiz
• Kişiselleştirilmiş öneriler
• Trend takibi
• Otomatik kategorizasyon
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    def _format_dict(self, data_dict):
        """Sözlüğü güzel formatlama"""
        if not data_dict:
            return "Veri yok"
        
        formatted = []
        for key, value in data_dict.items():
            bar = "▓" * min(value, 10)
            formatted.append(f"• {key}: {value} {bar}")
        
        return "\n".join(formatted)
    
    def _get_category_emoji(self, category):
        """Kategori emojisi"""
        emojis = {
            "teknoloji": "💻",
            "iş_dünyası": "💼", 
            "araştırma": "🔬",
            "ürün": "📱",
            "politika": "🏛️",
            "genel": "📰"
        }
        return emojis.get(category, "📰")
    
    def _get_sentiment_emoji(self, sentiment):
        """Duygu emojisi"""
        emojis = {
            "pozitif": "😊",
            "negatif": "😔", 
            "nötr": "😐"
        }
        return emojis.get(sentiment, "😐")

# Global AI asistan instance
ai_assistant = AIAssistant()

# Handler fonksiyonları
async def handle_ai_analysis(update, context):
    """Analiz komutu handler"""
    await ai_assistant.analyze_news_command(update, context)

async def handle_ai_summary(update, context):
    """Özet komutu handler"""
    await ai_assistant.smart_news_summary(update, context)

async def handle_ai_trends(update, context):
    """Trend komutu handler"""
    await ai_assistant.trend_analysis(update, context)

async def handle_ai_help(update, context):
    """AI yardım komutu handler"""
    await ai_assistant.ai_help(update, context)

# Haber kontrol fonksiyonları
async def manual_news_check(bot, chat_id):
    """Manuel haber kontrolü"""
    try:
        # news_tracker'dan import et
        from news_tracker import fetch_webtekno_news, fetch_donanimhaber_news
        
        # İki kaynaktan da haber al
        donanimhaber_news = fetch_donanimhaber_news()
        webtekno_news = fetch_webtekno_news()
        
        total_news = len(donanimhaber_news) + len(webtekno_news)
        
        response = f"""📰 **Manuel Haber Kontrolü**

🔍 **Donanım Haber:** {len(donanimhaber_news)} haber
🔍 **WebTekno:** {len(webtekno_news)} haber
📊 **Toplam:** {total_news} haber bulundu

✅ Veriler güncellendi!"""
        
        await bot.send_message(chat_id=chat_id, text=response, parse_mode='Markdown')
        
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Haber kontrol hatası: {e}")

def get_news_status():
    """Haber sistemi durumunu al"""
    try:
        import sqlite3
        db = sqlite3.connect('data/assistant.db')
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM ai_news")
        count = cursor.fetchone()[0]
        db.close()
        
        return f"Aktif - {count} haber kayıtlı"
    except:
        return "Durum alınamadı"
