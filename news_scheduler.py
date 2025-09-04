"""
Otomatik haber takip scheduler'ı
- 2 saatte bir haber kontrolü
- Telegram'a otomatik gönderim
"""
from apscheduler.schedulers.background import BackgroundScheduler
from news_tracker import check_and_send_news, get_unsent_news, mark_as_sent, send_news_to_telegram, init_news_db
import asyncio
import os

# Global değişkenler
news_scheduler = None
bot_instance = None
owner_chat_id = None

def init_news_scheduler(bot, chat_id):
    """Haber scheduler'ını başlat"""
    global news_scheduler, bot_instance, owner_chat_id
    
    bot_instance = bot
    owner_chat_id = chat_id
    
    # Veritabanını hazırla
    init_news_db()
    
    # Scheduler'ı başlat
    news_scheduler = BackgroundScheduler(timezone='Europe/Istanbul')
    
    # 2 saatte bir haber kontrolü
    news_scheduler.add_job(
        scheduled_news_check,
        'interval',
        hours=2,
        id='news_checker',
        replace_existing=True
    )
    
    # İlk kontrolü hemen yap
    news_scheduler.add_job(
        scheduled_news_check,
        'date',
        id='initial_news_check',
        replace_existing=True
    )
    
    news_scheduler.start()
    print("📰 Haber takip sistemi başlatıldı! 2 saatte bir kontrol edilecek.")
    print("📡 Aktif Kaynaklar: Donanım Haber + WebTekno")
    print("⏰ İlk kontrol şimdi başlatılacak...")

def scheduled_news_check():
    """Zamanlı haber kontrolü"""
    try:
        print("🔍 Otomatik haber kontrolü başlatıldı...")
        
        # Yeni haberleri kontrol et
        new_news = check_and_send_news()
        
        if new_news and bot_instance and owner_chat_id:
            # Yeni haberleri Telegram'a gönder
            asyncio.run(send_news_batch(new_news))
        
    except Exception as e:
        print(f"❌ Otomatik haber kontrolü hatası: {e}")

async def send_news_batch(news_list):
    """Haber listesini Telegram'a tek tek gönder"""
    try:
        for news in news_list:
            success = await send_news_to_telegram(bot_instance, owner_chat_id, news)
            if success:
                mark_as_sent(news.get('id'))
                print(f"✅ Haber gönderildi: [{news.get('source', 'Unknown')}] {news['title'][:50]}...")
                # Haberleri arasında 3 saniye bekle (spam önleme)
                await asyncio.sleep(3)
            else:
                print(f"❌ Haber gönderilemedi: [{news.get('source', 'Unknown')}] {news['title'][:50]}...")
                
    except Exception as e:
        print(f"❌ Haber gönderim hatası: {e}")

async def manual_news_check(bot, chat_id):
    """Manuel haber kontrolü (komut ile)"""
    try:
        await bot.send_message(chat_id, "🔍 Yapay zeka haberlerini kontrol ediyorum...")
        
        # Yeni haberleri kontrol et
        new_news = check_and_send_news()
        
        if new_news:
            await bot.send_message(chat_id, f"🆕 {len(new_news)} yeni haber bulundu! Gönderiyorum...")
            await send_news_batch(new_news)
            await bot.send_message(chat_id, "✅ Tüm yeni haberler gönderildi!")
        else:
            # Gönderilmemiş haberleri kontrol et
            unsent = get_unsent_news()
            if unsent:
                await bot.send_message(chat_id, f"📰 {len(unsent)} bekleyen haber var, gönderiyorum...")
                await send_news_batch(unsent)
            else:
                await bot.send_message(chat_id, "📭 Yeni haber bulunamadı.")
                
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Haber kontrolü hatası: {e}")

def stop_news_scheduler():
    """Haber scheduler'ını durdur"""
    global news_scheduler
    if news_scheduler:
        news_scheduler.shutdown()
        print("🛑 Haber takip sistemi durduruldu.")

def get_news_status():
    """Haber sistemi durumunu getir"""
    global news_scheduler
    if news_scheduler and news_scheduler.running:
        jobs = news_scheduler.get_jobs()
        return f"✅ Aktif - {len(jobs)} görev çalışıyor"
    else:
        return "❌ Durdurulmuş"
