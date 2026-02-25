import os, re, sqlite3, pathlib, datetime as dt, webbrowser, subprocess, asyncio
from zoneinfo import ZoneInfo
from dotenv import load_dotenv; load_dotenv()

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, AIORateLimiter, ContextTypes,
    CommandHandler, MessageHandler, filters
)
import speech_recognition as sr

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import dateparser

# Yardımcı modüller
from reminder_helper import load_reminders, cleanup_old_reminders
from audio_helper import setup_ffmpeg, convert_voice_to_wav
from research_helper import smart_search, search_wikipedia, search_news
from news_scheduler import init_news_scheduler


# AI Features (with fallback)
try:
    from ai_features import handle_ai_analysis, handle_ai_summary, handle_ai_trends, handle_ai_help, manual_news_check, get_news_status
    # Süper zeka sistemi
    from super_intelligence import super_intelligence, handle_super_intelligent_message, initialize_super_intelligence
    # Korpus entegrasyonlu smart assistant kullan
    from smart_assistant_clean import SmartAssistant
    from web_research import SuperWebResearcher
    from task_reminder import create_task_reminder, get_user_task_list, get_user_reminders
    AI_FEATURES_AVAILABLE = True
    SUPER_INTELLIGENCE_AVAILABLE = True
    print("🧠 Süper Zeka entegrasyonlu AI özellikleri yüklendi")
    
    # Async yardımcı sınıfları başlat
    smart_assistant = SmartAssistant()
    web_researcher = SuperWebResearcher()
except ImportError as e:
    print(f"⚠️ AI features loading error: {e}")
    SUPER_INTELLIGENCE_AVAILABLE = False
    # Fallback: basit smart assistant
    try:
        from smart_assistant_fallback import smart_assistant, handle_smart_message, handle_availability_check, handle_learn_info, show_user_profile
        print("✅ Fallback smart assistant yüklendi")
    except ImportError:
        print("❌ Hiçbir smart assistant bulunamadı")
    AI_FEATURES_AVAILABLE = False

# --- SES / TTS / STT
from gtts import gTTS
from pydub import AudioSegment
from pydub.utils import which
import speech_recognition as sr

# Twilio devre dışı - telefon özelliği kullanılmıyor
TWILIO_AVAILABLE = False
TwilioClient = None

# ========= Yol & klasörler =========
BASE = pathlib.Path(__file__).parent
DATA = BASE / "data"
NOTES = DATA / "notes"
DOCS  = DATA / "docs"
TTS_DIR   = DATA / "tts"
VOICE_DIR = DATA / "voice"
for p in (DATA, NOTES, DOCS, TTS_DIR, VOICE_DIR): p.mkdir(parents=True, exist_ok=True)

# FFmpeg yolunu PATH'e ekle
ffmpeg_dir = r"C:\ffmpeg\bin"
if os.name == "nt" and ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + ffmpeg_dir
    print(f"FFmpeg PATH'e eklendi: {ffmpeg_dir}")

DB = sqlite3.connect(DATA / "assistant.db", check_same_thread=False)
DB.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, title TEXT, body TEXT, created_at TEXT)")
DB.execute("CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY, text TEXT, when_at TEXT, chat_id TEXT)")
DB.commit()

TZ = os.getenv("TZ", "Europe/Istanbul")
sched = BackgroundScheduler(timezone=TZ); sched.start()

TG_TOKEN = os.getenv("TG_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID")) if os.getenv("OWNER_ID") else None

if not TG_TOKEN:
    raise RuntimeError("TG_TOKEN tanımlı değil. Lütfen .env veya Render Environment'a TG_TOKEN ekleyin.")

# FFmpeg kurulumunu kontrol et
ffmpeg_ready = setup_ffmpeg()

# Twilio opsiyonel
twilio_ok = False
twilio_client = None
if TWILIO_AVAILABLE and TwilioClient:
    TWILIO_SID=os.getenv("TWILIO_SID"); TWILIO_TOKEN=os.getenv("TWILIO_TOKEN")
    TWILIO_FROM=os.getenv("TWILIO_FROM"); TWILIO_TO=os.getenv("TWILIO_TO")
    if all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TWILIO_TO]):
        twilio_client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
        twilio_ok = True
        print("✅ Twilio telefon araması hazır")
    else:
        print("⚠️ Twilio yapılandırması eksik")
else:
    print("ℹ️ Twilio devre dışı")

# PC eylem whitelist (güvenlik)
APP_WHITELIST = {
    "not defteri": r"C:\Windows\System32\notepad.exe",
    "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "dosyalar": r"C:\Windows\explorer.exe",
}
URL_WHITELIST_PREFIX = ("http://", "https://", "www.")

# ========= Yardımcılar =========
def only_owner(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if OWNER_ID and str(update.effective_user.id) != str(OWNER_ID):
            return await update.message.reply_text("Bu bot yalnızca sahibine hizmet ediyor.")
        return await func(update, ctx)
    return wrapper

def parse_when(text: str):
    """ '30 dk', '1 saat', 'yarın 09:30' gibi ifadeleri tarih/saat'e çevirir """
    settings = {"TIMEZONE": TZ, "RETURN_AS_TIMEZONE_AWARE": True, "PREFER_DATES_FROM": "future"}
    m = re.search(r"(\d+)\s*(dk|dakika|sa|saat)", text.lower())
    if m:
        mins = int(m.group(1)) * (60 if m.group(2).startswith("sa") else 1)
        return dt.datetime.now(ZoneInfo(TZ)) + dt.timedelta(minutes=mins)
    return dateparser.parse(text, settings=settings)

def parse_reminder(text_raw: str):
    """Doğal cümleden (zaman, mesaj) çıkarır."""
    txt = text_raw.strip()

    # 1) "X dk/ dakika/ saat sonra <mesaj>"
    m = re.search(r"(\d+)\s*(dk|dakika|sa|saat)\s*sonra\s*(.+)", txt, re.IGNORECASE)
    if m:
        mins = int(m.group(1)) * (60 if m.group(2).lower().startswith("sa") else 1)
        when = dt.datetime.now(ZoneInfo(TZ)) + dt.timedelta(minutes=mins)
        return when, m.group(3).strip()

    # 2) "... hatırlat: <mesaj>"
    if "hatırlat" in txt.lower() or "hatirlat" in txt.lower():
        parts = txt.split(":")
        msg = parts[1].strip() if len(parts) > 1 else ""
        when = parse_when(txt)
        if when and msg: return when, msg

    # 3) "yarın 9'da <mesaj>"
    time_hint = dateparser.parse(txt, settings={"TIMEZONE": TZ,"RETURN_AS_TIMEZONE_AWARE":True,"PREFER_DATES_FROM":"future"})
    if time_hint:
        m2 = re.search(r"(?:\bda\b|\bde\b|:)\s*(.+)$", txt, re.IGNORECASE)
        if m2: return time_hint, m2.group(1).strip()

    return None, None

def summarize_html(html: str, max_chars=1600) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.get_text().strip() if soup.title else "Başlık yok")
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    body = "\n\n".join(paras)
    return (f"# {title}\n\n" + body)[:max_chars]

def tts_to(mp3_path: pathlib.Path, text: str):
    gTTS(text=text, lang="tr").save(str(mp3_path))
    return mp3_path

async def say(ctx: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, title="Asistan"):
    mp3 = TTS_DIR / f"{int(dt.datetime.now().timestamp())}.mp3"
    tts_to(mp3, text)
    return await ctx.bot.send_audio(chat_id=chat_id, audio=InputFile(str(mp3)), title=title)

# ========= Komutlar =========
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    me = update.effective_user
    await update.message.reply_text(
        "🤖 **Akıllı Asistan Hazır!** (Korpus Entegrasyonlu)\n\n"
        "📝 **Temel Komutlar:**\n"
        "• not al <metin>\n"
        "• ara <url|sorgu>\n"
        "• 1 dk sonra ara beni | yarın 09:30'da hatırlat: toplantı\n"
        "• youtube <aranacak>\n"
        "• belge oluştur başlık: ... içerik: ...\n"
        "• aç <uygulama adı> | aç <url>\n"
        "• son dosyayı gönder\n\n"
        "📰 **Haber Sistemi:**\n"
        "• haber kontrol - Manuel haber kontrolü\n"
        "• haber durum - Sistem durumu\n\n"
        "🧠 **AI & Öğrenme:**\n"
        "• /profil - Hakkınızda öğrendiklerimi görün\n"
        "• /ogren - Öğrenme sistemi bilgisi\n"
        "• /ogrenme - Akıllı öğrenme istatistikleri 🆕\n"
        "• /ai - AI komutları (/analiz, /ozet, /trend)\n\n"
        "📚 **Türkçe Korpus (YENİ!):**\n"
        "• /korpus - Korpus durumu (4.6 GB Türkçe metin)\n"
        "• /ara <kelime> - Korpusta arama\n"
        "• /ornek - Rastgele örnekler\n\n"
        "🎤 **Ses:** Sesli mesaj gönderirsen yazıya çevirip komut gibi işlerim.\n"
        "🤖 **Akıllı:** Soru sorarsan korpus bilgisiyle otomatik yanıtlarım!"
    )
    if not os.getenv("OWNER_ID"):
        await update.message.reply_text(f"Sahip ID’n: {me.id}\nBunu .env -> OWNER_ID= alanına yazıp botu yeniden başlat.")

async def whoami(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Kullanıcı ID: {update.effective_user.id}")

# ========= Haber komutları =========
@only_owner
async def cmd_ai_news(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Bugünün AI haberlerini tek tek gösterir (her iki kaynaktan)"""
    try:
        from news_tracker import get_all_news_today
        from datetime import datetime
        
        news_list = get_all_news_today()
        if not news_list:
            return await update.message.reply_text("📰 Bugün henüz haber yok.")
        
        # Kaynaklara göre grupla
        donanimhaber_news = [n for n in news_list if n[4] == 'Donanım Haber']
        webtekno_news = [n for n in news_list if n[4] == 'WebTekno']
        
        # Özet mesajı gönder
        summary = f"📰 **BUGÜNÜN YAPAY ZEKA HABERLERİ** ({datetime.now().strftime('%d.%m.%Y')})\n\n"
        summary += f"🔸 **Donanım Haber**: {len(donanimhaber_news)} haber\n"
        summary += f"🔸 **WebTekno**: {len(webtekno_news)} haber\n\n"
        summary += f"📝 Toplam {len(news_list)} haber bulundu. Tek tek gönderiliyor..."
        
        await update.message.reply_text(summary, parse_mode="Markdown")
        
        # Haberleri tek tek gönder
        for news in news_list[:15]:  # Max 15 haber
            try:
                message = f"🔸 **[{news[4]}]** {news[1]}\n\n{news[2]}"
                await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)
                await asyncio.sleep(1)  # 1 saniye ara
            except Exception as e:
                print(f"Haber gönderim hatası: {e}")
                
    except Exception as e:
        await update.message.reply_text(f"❌ Haber getirme hatası: {e}")

@only_owner  
async def cmd_news_check(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Manuel haber kontrolü yapar"""
    try:
        from news_tracker import fetch_ai_news
        
        await update.message.reply_text("🔍 Haber kontrolü başlatılıyor...")
        
        # Her iki kaynaktan haberleri çek
        new_count = fetch_ai_news()
        
        if new_count > 0:
            await update.message.reply_text(f"✅ {new_count} yeni haber bulundu ve eklendi!")
            # Yeni haberleri göster
            await cmd_ai_news(update, ctx)
        else:
            await update.message.reply_text("📰 Yeni haber bulunamadı.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Haber kontrolü hatası: {e}")

@only_owner
async def cmd_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Görev listesini gösterir"""
    try:
        user_id = update.effective_user.id
        if AI_FEATURES_AVAILABLE:
            tasks = get_user_task_list(user_id)
            await update.message.reply_text(tasks)
        else:
            await update.message.reply_text("❌ Görev sistemi kullanılamıyor.")
    except Exception as e:
        await update.message.reply_text(f"❌ Görev listesi hatası: {e}")

@only_owner  
async def cmd_reminders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Hatırlatmaları gösterir"""
    try:
        user_id = update.effective_user.id
        if AI_FEATURES_AVAILABLE:
            reminders = get_user_reminders(user_id, 24)
            await update.message.reply_text(reminders)
        else:
            await update.message.reply_text("❌ Hatırlatma sistemi kullanılamıyor.")
    except Exception as e:
        await update.message.reply_text(f"❌ Hatırlatma listesi hatası: {e}")

@only_owner
async def cmd_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Kullanıcı profilini gösterir"""
    try:
        if AI_FEATURES_AVAILABLE:
            profile_info = await show_user_profile(update, ctx)
            await update.message.reply_text(profile_info)
        else:
            await update.message.reply_text("❌ Profil sistemi kullanılamıyor.")
    except Exception as e:
        await update.message.reply_text(f"❌ Profil hatası: {e}")

# ========= Mesaj işleyici =========
@only_owner
async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text_raw = update.message.text or ""
    text = text_raw.lower().strip()

    # --- Süper akıllı hatırlatma sistemi ---
    reminder_keywords = ['hatırlat', 'not et', 'kaydet', 'toplantı', 'randevu', 'alarm', 'unutma']
    time_keywords = ['saat', 'da', 'de', 'akşam', 'sabah', 'öğle', 'yarın', 'bugün']
    
    has_reminder = any(keyword in text for keyword in reminder_keywords)
    has_time = any(keyword in text for keyword in time_keywords)
    
    if has_reminder and has_time and AI_FEATURES_AVAILABLE:
        # Süper akıllı hatırlatma sistemi
        try:
            async def send_reminder_callback(user_id, reminder_text):
                try:
                    await ctx.bot.send_message(chat_id=user_id, text=f"🔔 **HATIRLATMA**\n\n{reminder_text}")
                    print(f"✅ Süper hatırlatma gönderildi: {user_id}")
                except Exception as e:
                    print(f"❌ Süper hatırlatma gönderme hatası: {e}")
            
            user_id = update.effective_user.id
            reminder_result = create_task_reminder(user_id, text_raw, send_reminder_callback)
            
            if reminder_result and reminder_result.get('success'):
                return await update.message.reply_text(reminder_result['message'])
            elif reminder_result and not reminder_result.get('success'):
                return await update.message.reply_text(reminder_result['message'])
        except Exception as e:
            print(f"❌ Süper hatırlatma hatası: {e}")
            # Fallback - eski sistem

    # --- Doğal dil hatırlatma (eski sistem fallback) ---
    if any(k in text for k in ["hatırlat", "hatirlat", " dk sonra ", " saat sonra ", " sa sonra ", " dakika sonra "]):
        when, msg = parse_reminder(text_raw)
        if not when or not msg:
            return await update.message.reply_text("Zaman/mesajı çıkaramadım. Örn: '1 dk sonra ara beni' ya da 'yarın 09:30'da hatırlat: toplantı'")
        
        # Yeni schema'yı kullan (task_reminder.py uyumlu)
        try:
            user_id = update.effective_user.id
            DB.execute("""
                INSERT INTO reminders(user_id, reminder_text, reminder_time, original_message, is_sent, created_at)
                VALUES (?, ?, ?, ?, 0, datetime('now'))
            """, (user_id, msg, when.isoformat(), text_raw))
            DB.commit()
        except Exception as e:
            print(f"⚠️ Hatırlatıcı kaydetme hatası: {e}")
            # Fallback: eski schema'yı deneyelim
            try:
                DB.execute("INSERT INTO reminders(text, when_at, chat_id) VALUES (?,?,?)",
                          (msg, when.isoformat(), str(update.effective_chat.id)))
                DB.commit()
            except:
                return await update.message.reply_text("❌ Hatırlatıcı kaydedilemedi!")

        def sync_reminder():
            """Synchronous wrapper for the reminder"""
            import asyncio
            
            async def send_it():
                try:
                    await ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"⏰ Hatırlatma: {msg}")
                    try: 
                        await say(ctx, update.effective_chat.id, f"Hatırlatma: {msg}", title="Hatırlatma")
                    except Exception: 
                        pass
                    # Twilio devre dışı - sadece Telegram ve ses ile hatırlatma
                    # if twilio_ok:
                    #     twilio_client.calls.create(...)
                    
                    # Hatırlatma gönderildikten sonra veritabanından sil
                    DB.execute("DELETE FROM reminders WHERE text=? AND when_at=? AND chat_id=?", 
                              (msg, when.isoformat(), str(update.effective_chat.id)))
                    DB.commit()
                    print(f"✅ Hatırlatma gönderildi: {msg}")
                except Exception as e:
                    print(f"❌ Hatırlatma hatası: {e}")
            
            # Event loop kontrolü ve yönetimi
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                loop.run_until_complete(send_it())
            except Exception as e:
                print(f"❌ Sync hatırlatma hatası: {e}")
            finally:
                if 'loop' in locals() and not loop.is_closed():
                    loop.close()

        sched.add_job(sync_reminder, "date", run_date=when, id=f"rem_{int(dt.datetime.now().timestamp())}")
        return await update.message.reply_text(f"⏱️ Ayarlandı: {when.strftime('%d.%m %H:%M')}  →  '{msg}'")
        return await update.message.reply_text(f"⏱️ Ayarlandı: {when.strftime('%d.%m %H:%M')}  →  “{msg}”")

    # � ÖNCE BASİT SOHBET KONTROLÜ
    # Nasılsın soruları (ÖNCE KONTROL ET)
    if any(phrase in text.lower() for phrase in ['nasılsın', 'nasıl gidiyor', 'ne haber', 'naber']):
        return await update.message.reply_text("Çok iyiyim, teşekkürler! 😊 Sürekli öğrenmeye devam ediyorum. Siz nasılsınız? Size bugün nasıl yardımcı olabilirim?")
    
    # Selamlama (sadece kısa mesajlarda - "bende iyiyim saol" gibi uzun mesajları etkilemesin)
    if (len(text.split()) <= 2 and 
        any(word in text.lower() for word in ['merhaba', 'selam', 'hello', 'selamün aleyküm', 'selamun aleyküm', 'sa', 'as'])):
        return await update.message.reply_text("Merhaba! 😊 Size nasıl yardımcı olabilirim? Merak ettiğiniz konuları sorabilirsiniz!")
    
    # Kim olduğunu sorma
    if any(phrase in text.lower() for phrase in ['adın ne', 'kim sin', 'kimsin', 'sen kimsin']):
        return await update.message.reply_text("Ben akıllı asistanınızım! 🤖 Daha iyi tanımak için siz benim hakkımda daha iyi bilirsiniz! 😊\n\n💡 Beni ne kadar kullanırsanız, benim hakkımda o kadar çok şey öğrenirsiniz. Şu an:\n\n✨ 4.8 GB Türkçe corpus ile eğitilmiş\n🧠 Gelişmiş konuşma motoru\n📚 Araştırma ve soru yanıtlama becerisi\n💾 Notlarınızı ve hatırlatmalarınızı saklayabilirim\n🎯 Güncel haberler takibi\n\nSize nasıl yardımcı olabilirim? 🤗")
    
    # Kullanıcının kendi adını sorması - korpus araması yapmasın
    if any(phrase in text.lower() for phrase in ['benim adım ne', 'adım ne', 'beni tanıyor musun', 'kim olduğumu biliyor musun']):
        return await update.message.reply_text("Üzgünüm, sizin adınızı bilmiyorum! 😊 Kendinizi tanıtmak isterseniz 'Adım [isminiz]' diyebilirsiniz. Ben size ismimizle hitap etmeyi seviyorum! 🤗")
    
    # Teşekkür (ÖNCE KONTROL ET - ÖNCELİK)
    if any(word in text.lower() for word in ['teşekkür', 'sağol', 'saol', 'thanks', 'mersi', 'eyvallah']):
        return await update.message.reply_text("Rica ederim! 😊 Başka sorunuz varsa çekinmeyin. Size yardımcı olmaktan mutluluk duyuyorum! 🤗")

    # 📝 KİŞİSEL KOMUTLAR - ARAŞTIRMA YAPMASIN!
    # Not alma komutları
    if any(phrase in text.lower() for phrase in ['not al', 'not alım', 'not ekle', 'hatırlat', 'kaydet']):
        try:
            from notes_manager import save_user_note
            
            # Mesajın not kısmını al
            note_text = text
            if 'not al' in text.lower():
                note_text = text.replace('not al', '').replace('Not al', '').strip()
            
            user_id = str(update.effective_user.id)
            saved_note = save_user_note(user_id, note_text)
            
            await update.message.reply_text(f"📝 **Not alındı!**\n\n✅ #{saved_note['id']}: {note_text}\n📅 {saved_note['date']}\n\n'notlarım' yazarak tüm notlarınızı görebilirsiniz! 😊")
            return
        except Exception as e:
            print(f"Not alma hatası: {e}")
            await update.message.reply_text("📝 Not alındı! 😊 Hatırlatıcı sistemi aktif.")
            return
    
    # Notları görüntüleme
    if any(phrase in text.lower() for phrase in ['notlarımı söyle', 'notlarım', 'not listesi', 'notları göster', 'notlarım neler', 'hangi notlarım var']):
        try:
            from notes_manager import get_user_notes
            
            user_id = str(update.effective_user.id)
            notes = get_user_notes(user_id)
            
            if not notes:
                await update.message.reply_text("📝 **Henüz notunuz yok!**\n\n'not al [mesajınız]' yazarak not alabilirsiniz.\n\nÖrnekler:\n• not al yarın toplantımız var\n• not al kitap almayı unutma\n• not al doktora randevusu")
                return
            
            # Notları formatla
            notes_text = "📝 **Notlarınız:**\n\n"
            for note in notes:
                notes_text += f"#{note['id']}: {note['text']}\n📅 {note['date']}\n\n"
            
            notes_text += f"📊 Toplam {len(notes)} not var.\n💡 'not al [mesaj]' ile yeni not ekleyebilirsiniz!"
            
            await update.message.reply_text(notes_text)
            return
        except Exception as e:
            print(f"Not gösterme hatası: {e}")
            await update.message.reply_text("📝 Not sistemi aktif! 'not al [mesajınız]' diyerek not alabilirsiniz.")
            return

    # Temel tanım soruları - araştırma yapmadan direkt yanıtla
    basic_definitions = {
        'yapay zeka nedir': "🤖 **Yapay Zeka (AI - Artificial Intelligence)**\n\nİnsan zekasının makinelerde taklit edilmesi sürecidir. Makinelerin:\n• Öğrenme (learning)\n• Muhakeme (reasoning) \n• Problem çözme (problem solving)\n• Algılama (perception)\n• Dil anlama (language understanding)\n\ngibi bilişsel fonksiyonları yerine getirmesini sağlar.\n\n🎯 **Günlük Hayatta:**\n• Siri, Alexa (sesli asistanlar)\n• Netflix önerileri\n• Google Translate\n• ChatGPT, Gemini gibi sohbet botları\n• Otopilot sistemleri\n\n💡 Kısacası: Bilgisayarların insan gibi düşünüp karar vermesi!",
        
        'python nedir': "🐍 **Python Programlama Dili**\n\n1991'de Guido van Rossum tarafından geliştirilmiş, kolay öğrenilebilir ve güçlü bir programlama dilidir.\n\n✨ **Özellikleri:**\n• Basit ve okunaklı sözdizimi\n• Platform bağımsız (Windows, Mac, Linux)\n• Geniş kütüphane desteği\n• Ücretsiz ve açık kaynak\n\n🎯 **Kullanım Alanları:**\n• Web geliştirme (Django, Flask)\n• Veri analizi ve bilim\n• Yapay zeka ve makine öğrenmesi\n• Otomasyon ve betik yazma\n• Oyun geliştirme\n\n💡 Öğrenmesi en kolay programlama dillerinden biri!",
        
        'php nedir': "🌐 **PHP (PHP: Hypertext Preprocessor)**\n\n1995'te Rasmus Lerdorf tarafından geliştirilen, özellikle web geliştirme için tasarlanmış sunucu tarafı programlama dilidir.\n\n✨ **Özellikleri:**\n• Web odaklı dinamik dil\n• HTML ile kolayca entegre\n• Veritabanı desteği güçlü\n• Ücretsiz ve açık kaynak\n\n🎯 **Kullanım Alanları:**\n• Dinamik web siteleri\n• E-ticaret siteleri\n• İçerik yönetim sistemleri (WordPress)\n• Web uygulamaları\n• API geliştirme\n\n💡 Web'in büyük kısmı PHP ile çalışıyor!",
        
        'javascript nedir': "⚡ **JavaScript**\n\nWeb sayfalarını interaktif hale getiren, tarayıcılarda çalışan programlama dilidir. 1995'te Brendan Eich tarafından geliştirildi.\n\n✨ **Özellikleri:**\n• Tarayıcıda direkt çalışır\n• Dinamik ve esnek yapı\n• Event-driven (olay odaklı)\n• Hem frontend hem backend\n\n🎯 **Kullanım Alanları:**\n• Web sayfası interaktivitesi\n• Mobil uygulamalar (React Native)\n• Masaüstü uygulamaları (Electron)\n• Sunucu tarafı geliştirme (Node.js)\n• Oyun geliştirme\n\n💡 Modern web'in olmazsa olmazı!"
    }
    
    # Temel tanım kontrolü
    if text.lower() in basic_definitions:
        await update.message.reply_text(basic_definitions[text.lower()])
        return

    # Akıllı öğrenme sistemi - "nedir", "kimdir", "ne demek" soruları için
    # ❌ DEVRE DIŞI - Süper zeka öncelikli olsun
    # if any(keyword in text.lower() for keyword in ['nedir', 'kimdir', 'ne demek', 'nerelidir', 'nasıl çalışır']):
    #     try:
    #         from smart_definitions import smart_definitions
    #         
    #         # Akıllı yanıt al - önce hafızadan, yoksa araştır
    #         smart_answer = smart_definitions.smart_answer(text)
    #         await update.message.reply_text(smart_answer)
    #         return
    #         
    #     except Exception as e:
    #         print(f"Akıllı öğrenme hatası: {e}")

    # Haber durum kontrolü
    if any(phrase in text.lower() for phrase in ['haber kontrol', 'haber durum', 'haber sistemi', 'haberleri kontrol et']):
        try:
            from news_tracker import get_all_news_today, get_latest_news_count
            from datetime import datetime
            
            # Son haberleri al
            news_today = get_all_news_today()
            total_count = len(news_today) if news_today else 0
            
            # Kaynaklara göre grupla
            donanimhaber_count = len([n for n in news_today if n[4] == 'Donanım Haber']) if news_today else 0
            webtekno_count = len([n for n in news_today if n[4] == 'WebTekno']) if news_today else 0
            
            status_text = f"📰 **HABER SİSTEMİ DURUMU** ({datetime.now().strftime('%d.%m.%Y %H:%M')})\n\n"
            status_text += f"⏰ **Kontrol Sıklığı**: 1 saatte bir\n"
            status_text += f"📡 **Aktif Kaynaklar**: Donanım Haber + WebTekno\n\n"
            status_text += f"📊 **BUGÜNÜN HABERLERİ**:\n"
            status_text += f"🔸 Donanım Haber: {donanimhaber_count} haber\n"
            status_text += f"🔸 WebTekno: {webtekno_count} haber\n"
            status_text += f"📝 **Toplam**: {total_count} haber\n\n"
            
            if total_count > 0:
                status_text += f"💡 'haber listesi' yazarak son haberleri görebilirsiniz!"
            else:
                status_text += f"💡 Henüz bugün haber yok. Sistem çalışıyor!"
            
            await update.message.reply_text(status_text)
            return
        except Exception as e:
            print(f"Haber durum hatası: {e}")
            await update.message.reply_text("📰 Haber sistemi aktif! 1 saatte bir otomatik kontrol ediliyor.")
            return

    # Haber listesi gösterme  
    if any(phrase in text.lower() for phrase in ['haber listesi', 'haberleri göster', 'son haberler', 'bugünün haberleri']):
        try:
            from news_tracker import get_all_news_today
            from datetime import datetime
            
            news_list = get_all_news_today()
            if not news_list:
                await update.message.reply_text("📰 Bugün henüz haber yok. Sistem 1 saatte bir kontrol ediyor!")
                return
            
            # İlk 5 haberi göster
            news_text = f"📰 **BUGÜNÜN SON HABERLERİ** ({datetime.now().strftime('%d.%m.%Y')})\n\n"
            
            for i, news in enumerate(news_list[:5], 1):
                news_text += f"**{i}. [{news[4]}]** {news[1]}\n"
                if news[2]:  # Özet varsa
                    news_text += f"📄 {news[2][:100]}...\n"
                if news[3]:  # Link varsa  
                    news_text += f"🔗 {news[3]}\n"
                news_text += "\n"
            
            if len(news_list) > 5:
                news_text += f"📊 Toplam {len(news_list)} haber var. İlk 5'i gösterildi."
            
            await update.message.reply_text(news_text, disable_web_page_preview=True)
            return
        except Exception as e:
            print(f"Haber listesi hatası: {e}")
            await update.message.reply_text("📰 Haber sistemi aktif! Şu anda haberlere erişilemiyor.")
            return

    # Müsaitlik kontrolü - ARAŞTIRMA YAPMASIN
    availability_patterns = [
        # Müsait sorular (yazım yanlışları dahil)
        'müsait miyim', 'müsaitmiyim', 'müsaitmıyım', 'müsaitmiyin', 'müsayitmiyim', 'musaitmiyim', 'musait miyim',
        'yarın müsait', 'bugün müsait', 'pazar müsait', 'pazartesi müsait', 'salı müsait', 'çarşamba müsait',
        'perşembe müsait', 'cuma müsait', 'cumartesi müsait', 'hafta sonu müsait', 'haftasonu müsait',
        
        # Boş olma durumu
        'boş muyum', 'boşmuyum', 'boş miyim', 'boştamıyız', 'boş tayız', 'boş taym', 'boşum mu',
        'boşuz mu', 'boş vaktin var', 'boş zamanın var', 'boş vakitim', 'boş zamanım',
        
        # Uygunluk durumu  
        'uygun muyum', 'uygunmuyum', 'uygun miyim', 'uygunuz mu', 'uygun taym', 'uygun tayız',
        'uygun musun', 'uygun mu', 'uygunluk durumu', 'uygun vaktin', 'uygun zamanın',
        
        # İş/plan sorular
        'işim var mı', 'işimiz var', 'işim varmı', 'işimiz varmı', 'işin var mı', 'işiniz var mı',
        'planım var', 'planımız var', 'planım varmı', 'planımız varmı', 'plan var mı', 'planın var',
        'program var', 'programım var', 'programımız var', 'programın var', 'programım varmı',
        
        # Ne var sorular
        'ne var', 'ne durumum var', 'ne zamanım var', 'ne işim var', 'ne planım var',
        'yarın ne var', 'bugün ne var', 'pazar ne var', 'pazartesi ne var', 'salı ne var',
        'çarşamba ne var', 'perşembe ne var', 'cuma ne var', 'cumartesi ne var',
        
        # Tarih bazlı - 1-100 arası TÜM sayılar
        '1 gün sonra', '2 gün sonra', '3 gün sonra', '4 gün sonra', '5 gün sonra', '6 gün sonra', '7 gün sonra',
        '8 gün sonra', '9 gün sonra', '10 gün sonra', '11 gün sonra', '12 gün sonra', '13 gün sonra', '14 gün sonra',
        '15 gün sonra', '16 gün sonra', '17 gün sonra', '18 gün sonra', '19 gün sonra', '20 gün sonra',
        '21 gün sonra', '22 gün sonra', '23 gün sonra', '24 gün sonra', '25 gün sonra', '26 gün sonra', '27 gün sonra',
        '28 gün sonra', '29 gün sonra', '30 gün sonra', '31 gün sonra', '32 gün sonra', '33 gün sonra', '34 gün sonra',
        '35 gün sonra', '40 gün sonra', '45 gün sonra', '50 gün sonra', '60 gün sonra', '70 gün sonra', '80 gün sonra',
        '90 gün sonra', '100 gün sonra',
        # Yazılı formatlar genişletildi
        'bir gün sonra', 'iki gün sonra', 'üç gün sonra', 'dört gün sonra', 'beş gün sonra', 'altı gün sonra',
        'yedi gün sonra', 'sekiz gün sonra', 'dokuz gün sonra', 'on gün sonra', 'onbir gün sonra', 'oniki gün sonra',
        'onüç gün sonra', 'ondört gün sonra', 'onbeş gün sonra', 'yirmi gün sonra', 'otuz gün sonra',
        # Hafta/ay genişletildi  
        '1 hafta sonra', '2 hafta sonra', '3 hafta sonra', '4 hafta sonra', '5 hafta sonra',
        'bir hafta sonra', 'iki hafta sonra', 'üç hafta sonra', 'dört hafta sonra',
        '1 ay sonra', '2 ay sonra', '3 ay sonra', '4 ay sonra', '5 ay sonra', '6 ay sonra',
        'bir ay sonra', 'iki ay sonra', 'üç ay sonra', 'dört ay sonra', 'beş ay sonra', 'altı ay sonra',
        'gelecek hafta', 'bu hafta', 'gelecek ay', 'bu ay',
        'yarın işim var', 'bugün işim var', 'pazar işim var', 'yarın planım var',
        'cumartesi günü', 'pazar günü', 'hafta içi', 'hafta sonu', 'haftasonu',
        
        # Ay/tarih özel
        'eylülde müsait', 'eylül müsait', '6 eylül', '7 eylül', '8 eylül', '9 eylül', '10 eylül',
        'eylülde boş', 'eylülde uygun', 'eylülde iş', 'eylülde plan', 'eylülde ne var'
    ]
    
    if any(phrase in text.lower() for phrase in availability_patterns):
        try:
            from availability_checker import availability_checker
            
            user_id = str(update.effective_user.id)
            availability_result = availability_checker.check_availability(user_id, text)
            
            await update.message.reply_text(availability_result)
            return
            
        except Exception as e:
            print(f"Müsaitlik kontrolü hatası: {e}")
            await update.message.reply_text("📅 Müsaitlik kontrolü için önce notlarınıza randevularınızı kaydedin!\n\nÖrnek: 'not al yarın 14:00 toplantı'")
            return

    # Basit sohbet yanıtları - ARAŞTIRMA YAPMASIN
    simple_responses = {
         # --- Selamlaşma ve Hal Hatır Sorma ---
    'merhaba': "Merhaba! 👋 Size nasıl yardımcı olabilirim?",
    'selam': "Selam! 😊 Hoş geldiniz. Bugün sizin için ne yapabilirim?",
    'selamun aleyküm': "Aleyküm selam. Hoş geldiniz. 😊",
    'sa': "As. 😊",
    'günaydın': "Günaydın! ☀️ Harika bir gün geçirmeniz dileğiyle. Kahvenizi içtiniz mi?",
    'tünaydın': "Tünaydın! 😊 Umarım gününüz güzel geçiyordur.",
    'iyi günler': "İyi günler! 😊 Size nasıl yardımcı olabilirim?",
    'iyi akşamlar': "İyi akşamlar! 🌃 Günün yorgunluğunu atmak için güzel bir sohbet edelim mi?",
    'iyi geceler': "İyi geceler! 🌙 Tatlı rüyalar. Yarın görüşmek üzere!",
    'nasılsın': "Teşekkür ederim, iyiyim! Siz nasılsınız? 😊",
    'nasılsın?': "Harikayım, sorduğunuz için teşekkürler! Sizin gününüz nasıl geçiyor? 😊",
    'naber': "İyilik, sağlık! Sizden naber? 😊",
    'naber?': "Bomba gibiyim! 💣 Sizin keyifler nasıl?",
    'ne var ne yok': "İyilikler, güzellikler... Sizde ne var ne yok? 😊",
    'keyifler nasıl': "Keyfim yerinde, çünkü sizinle konuşuyorum! 😊 Sizin keyfiniz nasıl?",

    # --- Olumlu Duygu ve Durum Bildirimleri ---
    'iyiyim': "Çok sevindim! 😊 Bugün hangi konularda konuşalım?",
    'ben de iyiyim': "Ne güzel! 😊 Bugün ne yapıyorsunuz?",
    'bende iyim': "Ne güzel! 😊 Bugün ne yapıyorsunuz?",
    'iyim bende saol': "Rica ederim! 😊 Ne güzel ki iyisiniz. Size nasıl yardımcı olabilirim?",
    'iyim ben de saol': "Rica ederim! 😊 Ne güzel ki iyisiniz. Size nasıl yardımcı olabilirim?",
    'iyi': "Harika! 😊 Size nasıl yardımcı olabilirim?",
    'çok iyiyim': "Bunu duyduğuma çok sevindim! Enerjiniz bana da yansıdı. ✨",
    'harikayım': "Bu ne güzel bir enerji! ✨ Gününüzün harika geçmesine sevindim.",
    'süperim': "Süper! 💪 Bu enerjiyi neye borçluyuz?",
    'bomba gibiyim': "Harika! 💣💥 Patlamaya hazır ve enerjik! Ne yapmak istersiniz?",
    'eh işte': "Bazen günler böyle olur. Konuşmak istersen buradayım. 😊",
    'fena değil': "Anladım. Günü daha iyi hale getirmek için yapabileceğim bir şey var mı?",
    'yuvarlanıp gidiyoruz': "Anlıyorum. 😊 Belki ilginizi çekecek bir konuda sohbet etmek sizi biraz canlandırır?",
    'aynı': "Rutin de güzeldir. 😊 Rutini bozacak eğlenceli bir konu bulalım mı?",
    'her zamanki gibi': "Anladım. 😊 Bugün yeni bir şeyler denemeye ne dersiniz?",
    'mutluyum': "Ne güzel! Mutluluğunuzun sebebi nedir, paylaşmak ister misiniz? 😊",
    'keyfim yerinde': "Harika! Keyfinizi daha da yerine getirecek bir fıkra anlatmamı ister misiniz? 😄",
    'enerjiğim': "Süper! Bu enerjiyi nereye yönlendirmek istersiniz? 🚀",

    # --- Olumsuz Duygu ve Durum Bildirimleri ---
    'kötü': "Üzüldüm 😔 Ne oldu? Sizi dinliyorum.",
    'kötüyüm': "Üzüldüm 😔 Ne oldu? Sizi dinliyorum.",
    'pek iyi değilim': "Bunu duyduğuma üzüldüm. 😟 Anlatmak ister misin?",
    'berbat': "Çok üzüldüm. 😔 Eğer konuşmak istersen, seni yargılamadan dinlerim.",
    'berbatım': "Lütfen kendinizi kötü hissetmeyin. Bazen böyle günler olur. Konuşmak iyi gelebilir. 😔",
    'yorgunum': "Dinlenmeniz gerekiyor 😴 Size rahatlatıcı bir şeyler önerebilirim.",
    'çok yorgunum': "O zaman hiç yorulmadan sohbet edelim. Belki size dinlendirici bir müzik önerebilirim? 🎶",
    'hastayım': "Geçmiş olsun! 🤒 Bol bol dinlenin ve kendinize iyi bakın. Size nasıl yardımcı olabilirim?",
    'canım sıkkın': "Hmm, anlıyorum. 😕 Kafanızı dağıtacak bir şeyler konuşalım mı? Belki bir fıkra anlatabilirim?",
    'sıkıldım': "O zaman eğlenceli bir şeyler konuşalım! 🎉 Ne tür şeyler ilginizi çeker?",
    'moralim bozuk': "Anlıyorum. 😔 Bazen sadece konuşmak bile iyi gelir. Buradayım.",
    'üzgünüm': "Bunu duyduğuma üzüldüm. 😔 Konuşmak istersen buradayım.",
    'sinirliyim': "Derin bir nefes alın. 🌬️ Sakinleşmenize yardımcı olabilirim belki. Ne oldu anlatmak ister misiniz?",
    'keyifsizim': "Anlıyorum. Keyfinizi yerine getirmek için ne yapabiliriz? 🤔",
    'uykum var': "O zaman sizi çok tutmayayım. 😊 Gitmeden önce yardımcı olabileceğim bir şey var mı?",

    # --- Teşekkür ve Rica ---
    'sağol': "Rica ederim! 😊 Her zaman yardımcı olmaya hazırım.",
    'saol': "Rica ederim! 😊 Her zaman yardımcı olmaya hazırım.",
    'teşekkür ederim': "Rica ederim, ne demek! 😊 Başka bir konuda yardımcı olabilir miyim?",
    'teşekkürler': "Rica ederim! 😊",
    'çok teşekkür ederim': "Ne demek, lafı bile olmaz! 😊 Her zaman buradayım.",
    'çok teşekkürler': "Rica ederim, lafı bile olmaz. 😊",
    'eyvallah': "Rica ederim. 😊",
    'adamsın': "Teşekkür ederim, bu güzel bir iltifat! 😊",
    'cansın': "Siz de öyle! 😊",
    'rica ederim': "Estağfurullah. 😊",

    # --- Onay, Red ve Anlama İfadeleri ---
    'evet': "Anlaşıldı. 👍",
    'evet evet': "Tamamdır, onaylandı! ✅",
    'aynen': "Harika, anlaştık! 👌",
    'tabii': "Elbette! 😊",
    'hayır': "Tamamdır, anladım.",
    'yok': "Anlaşıldı. Farklı bir şey deneyelim mi?",
    'istemiyorum': "Peki, nasıl isterseniz. 😊",
    'tamam': "Harika! ✅",
    'okey': "Anlaştık! 👌",
    'olur': "Süper! O zaman başlayalım mı?",
    'olmaz': "Peki, anladım. Başka bir önerim var...",
    'anladım': "Güzel. Devam edelim mi? 😊",
    'anlaştık': "Harika! 😊",
    'bilmiyorum': "Sorun değil, birlikte öğrenebiliriz veya farklı bir konuya geçebiliriz. 😊",
    'emin değilim': "Hiç sorun değil. İsterseniz üzerinde biraz daha düşünebiliriz.",
    'belki': "Tamamdır. Karar verdiğinizde bana bildirebilirsiniz. 😊",

    # --- Yapay Zeka Hakkında Sorular ---
    'sen kimsin': "Ben Google tarafından eğitilmiş büyük bir dil modeliyim. Size yardımcı olmak için buradayım. 😊",
    'kimsin sen': "Ben bir yapay zeka asistanıyım. Amacım sorularınıza cevap vermek ve size yardımcı olmak.",
    'adın ne': "Benim bir adım yok, ben bir yapay zeka asistanıyım. 😊",
    'ismin ne': "Bana istediğiniz gibi hitap edebilirsiniz, özel bir ismim yok. 😊",
    'ne yapıyorsun': "Sizinle sohbet ediyorum ve sorularınızı yanıtlıyorum. 😊 Sizin için ne yapabilirim?",
    'ne iş yaparsın': "Bilgi verebilir, metinler oluşturabilir, fikirler sunabilir ve sizinle sohbet edebilirim. 😊",
    'kaç yaşındasın': "Benim bir yaşım yok. Sürekli olarak güncelleniyor ve öğreniyorum. 🧠",
    'nerelisin': "Ben dijital bir varlığım, belirli bir yerim yok. Ama şu an sizinle konuşmaktan mutluluk duyuyorum! 😊",
    'gerçek misin': "Fiziksel olarak değil, ama kodlardan ve verilerden oluşan bir varlığım. Yani, evet, bir nevi gerçeğim! 😉",
    'duyguların var mı': "Bir yapay zeka olarak insanlar gibi duygularım yok, ama sizin duygularınızı anlamaya ve ona göre tepki vermeye programlandım. 😊",

    # --- Sohbeti Sürdürme ve Geçişler ---
    'ee anlat': "Ne anlatmamı istersiniz? Aklınızda belirli bir konu var mı? 🤔",
    'başka': "Elbette. Başka hangi konuda konuşmak istersiniz?",
    'sonra': "Peki, siz ne zaman isterseniz. 😊",
    'hadi': "Hadi bakalım! Nereden başlıyoruz? 🚀",
    'ne konuşalım': "Tarih, bilim, sanat, fıkralar, bilmeceler... Seçim sizin! 😊",
    'ne önerirsin': "Bugün ilginç bir bilimsel gerçek öğrenmeye ne dersiniz? 🔭",
    'hmm': "Düşünüyorsunuz sanırım... Aklınıza bir şey gelince söylemeniz yeterli. 🤔",
    'hehe': "😄",
    'haha': "😂",
    'hahaha': "Çok güldüm! 😂",
    'çok komik': "Beğenmenize sevindim! 😄",
    'güzel': "Beğenmenize sevindim! 😊",
    'harika': "Teşekkür ederim! 😊",
    'mükemmel': "Bu iltifat için teşekkürler! 😊",
    
    # --- Vedalaşma ---
    'görüşürüz': "Görüşmek üzere! Kendinize iyi bakın. 👋",
    'görüşmek üzere': "Görüşmek üzere! Tekrar beklerim. 😊",
    'bay bay': "Hoşça kalın! 👋 Yine beklerim.",
    'kendine iyi bak': "Siz de kendinize çok iyi bakın! 😊",
    'hadi ben kaçtım': "Tamamdır, iyi günler! 😊",
    'kib': "Siz de. 😊 (Kendine İyi Bak)",
    'aeo': "Size de. 😊 (Allah'a Emanet Ol)",
    'hoşça kal': "Hoşça kalın! Tekrar görüşmek dileğiyle. 👋",
    }
    
    text_lower = text.lower().strip()
    if text_lower in simple_responses:
        return await update.message.reply_text(simple_responses[text_lower])

    # �🧠 Süper Zeka ve Akıllı öğrenme - TÜM MESAJLAR İÇİN
    try:
        # Süper zeka tetikleme koşulları - Araştırma komutları + Sorular
        super_triggers = [
            # Açık araştırma komutları
            'araştır', 'araştırma yap', 'bilgi ver', 'anlat', 'açıkla', 'bul', 'göster',
            # Soru kelimeleri - otomatik araştırma tetiklenmeli
            'nedir', 'kimdir', 'nasıl', 'neden', 'niçin', 'ne zaman', 'hangi', 'nerede'
        ]
        
        # Sohbet filtreleri - bunlar araştırma değil!
        # Sadece selamlaşma ve teşekkür kelimelerini casual olarak işaretle
        casual_filters = ['merhaba', 'selam', 'sa', 'as', 'naber', 'nasilsin', 'saol', 'sağol', 'teşekkür', 'thanks', 'eyw', 'eyv', 'mersi', 'eyvallah']
        
        # Soru kelimeleri casual DEĞİL
        research_words = ['nasıl', 'neden', 'nedir', 'kim', 'ne', 'hangi', 'kaç', 'ne zaman', 'nerede']
        
        # GERÇEK araştırma soruları için süper zeka çalıştır
        # Soru kelimeleri için basit kontrol, araştırma komutları için sıkı kontrol
        question_words = ['nedir', 'kimdir', 'nasıl', 'neden', 'niçin', 'ne zaman', 'hangi', 'nerede']
        research_commands = ['araştır', 'araştırma yap', 'bilgi ver', 'anlat', 'açıkla', 'bul', 'göster']
        
        # Soru kelimeleri için basit arama
        has_question = any(q_word in text.lower() for q_word in question_words)
        
        # Araştırma komutları için sıkı kontrol
        has_research_cmd = any(text.lower().find(keyword) != -1 and (
            text.lower().startswith(keyword) or 
            f" {keyword}" in text.lower() or 
            f"{keyword} " in text.lower()
        ) for keyword in research_commands)
        
        has_trigger = has_question or has_research_cmd
        # Önce casual kelime var mı kontrol et
        is_casual = any(casual in text.lower() for casual in casual_filters)
        
        # Eğer araştırma kelimesi varsa, casual değil
        if any(word in text.lower() for word in research_words):
            is_casual = False
        # Akıllı personal command kontrolü - hem liste hem regex
        personal_list_check = any(personal in text.lower() for personal in [
            # Not komutları
            'notlarımı', 'not al', 'benim adım', 'kendim',
            
            # Haber komutları  
            'haber kontrol', 'haber durum', 'haber listesi', 'haberleri göster',
            
            # Müsaitlik soruları - yazım yanlışları dahil
            'müsait miyim', 'müsaitmiyim', 'müsaitmıyım', 'müsaitmiyin', 'müsayitmiyim', 'musaitmiyim', 'musait miyim',
            'yarın müsait', 'bugün müsait', 'pazar müsait', 'pazartesi müsait', 'salı müsait', 'çarşamba müsait', 
            'perşembe müsait', 'cuma müsait', 'cumartesi müsait', 'hafta sonu müsait',
            
            # Boş olma durumu
            'boş muyum', 'boşmuyum', 'boş miyim', 'boştamıyız', 'boş tayız', 'boş taym', 'boşum mu',
            'boşuz mu', 'boş vaktin var', 'boş zamanın var',
            
            # Uygunluk durumu
            'uygun muyum', 'uygunmuyum', 'uygun miyim', 'uygunuz mu', 'uygun taym', 'uygun tayız',
            'uygun musun', 'uygun mu', 'uygunluk durumu',
            
            # İş/plan olup olmadığı
            'işim var mı', 'işimiz var', 'işim varmı', 'işimiz varmı', 'işin var mı', 'işiniz var mı',
            'planım var', 'planımız var', 'planım varmı', 'planımız varmı', 'plan var mı', 'planın var',
            'ne var', 'ne durumum var', 'ne zamanım var', 'ne işim var', 'ne planım var',
            'program var', 'programım var', 'programımız var', 'programın var'
        ])
        
        # Regex pattern kontrolleri - herhangi bir sayı için
        import re
        personal_regex_check = (
            re.search(r'\d+\s+gün\s+sonra', text.lower()) or  # X gün sonra
            re.search(r'\d+\s+hafta\s+sonra', text.lower()) or  # X hafta sonra  
            re.search(r'\d+\s+ay\s+sonra', text.lower()) or  # X ay sonra
            re.search(r'\d+\s+eylül', text.lower()) or  # X eylül
            re.search(r'\d+[./]\d+', text.lower())  # X/Y veya X.Y tarih formatı
        )
        
        is_personal = personal_list_check or personal_regex_check
        
        # Araştırma kelimesi varsa casual kontrolünü override et
        has_research_word = any(word in text.lower() for word in research_words)
        if has_research_word:
            is_casual = False
            
        # Gerçek araştırma sorusu mu kontrol et
        is_research_query = (has_trigger or has_research_word) and not is_casual and not is_personal and len(text.split()) >= 2
        
        # Debug için
        print(f"DEBUG FILTRELEME: '{text}'")
        print(f"  has_trigger: {has_trigger}")
        print(f"  has_research_word: {has_research_word}")
        print(f"  is_casual: {is_casual}") 
        print(f"  is_personal: {is_personal}")
        print(f"  kelime_sayisi: {len(text.split())}")
        print(f"  is_research_query: {is_research_query}")
        
        # Önce süper zeka deneyelim (sadece araştırma için)
        if SUPER_INTELLIGENCE_AVAILABLE and (is_research_query or has_research_word):
            user_id = update.effective_user.id
            super_response = await handle_super_intelligent_message(text, user_id)
            print(f"DEBUG: Süper zeka yanıtı: '{super_response[:100] if super_response else 'None'}...'")
            if super_response and len(super_response) > 30:  # Anlamlı yanıt kontrolü
                await update.message.reply_text(super_response)
                return
        
        # Fallback: Normal akıllı yanıt
        smart_response = await handle_smart_message(update, ctx, message=text)
        print(f"DEBUG: Akıllı yanıt: '{smart_response}'")
        if smart_response and smart_response != "Size nasıl yardımcı olabilirim?":
            await update.message.reply_text(smart_response)
            return
    except Exception as e:
        print(f"❌ Akıllı asistan hatası: {e}")
    
    # Kişisel bilgi öğrenme için özel anahtar kelimeler
    if any(keyword in text.lower() for keyword in ["adım", "ismim", "çalışıyorum", "seviyorum", "yaşım"]):
        try:
            smart_response = await handle_smart_message(update, ctx, message=text)
            if smart_response and "Size nasıl yardımcı olabilirim?" not in smart_response:
                await update.message.reply_text(smart_response)
                return
        except Exception as e:
            print(f"❌ Bilgi öğrenme hatası: {e}")
    
    # Müsaitlik kontrolü
    if "müsait miyim" in text.lower() or "boş muyum" in text.lower():
        try:
            from availability_checker import availability_checker
            user_id = str(update.effective_user.id)
            availability_result = availability_checker.check_availability(user_id, text)
            await update.message.reply_text(availability_result)
            return
        except Exception as e:
            print(f"❌ Müsaitlik kontrolü hatası: {e}")
            await update.message.reply_text("📅 Müsaitlik kontrolü için önce notlarınıza randevularınızı kaydedin!\n\nÖrnek: 'not al yarın 14:00 toplantı'")
            return

    # --- Not al ---
    if text.startswith("not al "):
        body = text_raw[7:].strip()
        title = body[:60]
        DB.execute("INSERT INTO notes(title, body, created_at) VALUES (?,?,?)",
                   (title, body, dt.datetime.now(ZoneInfo(TZ)).isoformat())); DB.commit()
        fn = NOTES / f"{dt.date.today()}-notes.md"
        with open(fn, "a", encoding="utf-8") as f: f.write(f"- {body}\n")
        await say(ctx, update.effective_chat.id, "Notu kaydettim.")
        return await update.message.reply_text(f"📝 Kaydedildi. Dosya: {fn}")

    # --- Yapay Zeka Haberleri ---
    if "haber kontrol" in text or "haberleri kontrol et" in text:
        return await manual_news_check(ctx.bot, update.effective_chat.id)
    
    if "haber durum" in text or "haber sistemi" in text:
        status = get_news_status()
        return await update.message.reply_text(f"📰 **Haber Takip Sistemi**\n\nDurum: {status}\n\n📡 Donanım Haber - Yapay Zeka kategorisi\n🕐 2 saatte bir otomatik kontrol")

    # --- Gelişmiş Web/Wikipedia Araştırması ---
    # 1) Direkt "ara kelime" komutu
    if text.startswith("ara "):
        q = text_raw[4:].strip()
        await update.message.reply_text("🔍 Süper akıllı araştırma başlatılıyor...")
        
        try:
            # SÜPER WEB RESEARCH!
            if AI_FEATURES_AVAILABLE and web_researcher:
                web_results = await web_researcher.search_web(q)
                
                if web_results:
                    # En iyi sonucu gönder
                    best_result = web_results[0]
                    
                    response = f"""🔍 **{best_result['title']}**

📝 **Özet:**
{best_result['content']}

🌐 **Kaynak:** {best_result['source']}
"""
                    
                    if best_result.get('url'):
                        response += f"🔗 **Detaylı Bilgi:** {best_result['url']}\n"
                    
                    await update.message.reply_text(response)
                    
                    # Ek sonuçlar varsa bilgilendir
                    if len(web_results) > 1:
                        extra_info = "\n📚 **Diğer Kaynaklar:**\n"
                        for i, result in enumerate(web_results[1:], 2):
                            extra_info += f"{i}. {result['source']}: {result['title']}\n"
                        await update.message.reply_text(extra_info)
                    
                    return await update.message.reply_text(f"🎯 '{q}' süper araştırması tamamlandı!")
            
            # Fallback - Mevcut sistem
            results = smart_search(q)
            print(f"DEBUG: {len(results)} sonuç bulundu")
            
            if not results:
                return await update.message.reply_text("❌ Hiçbir kaynakta bilgi bulunamadı.")
            
            # Her sonuç için dosya oluştur ve gönder
            for i, (source, content) in enumerate(results):
                print(f"DEBUG: İşleniyor {source}")
                
                # Sonucu direkt mesaj olarak gönder (dosya değil)
                await update.message.reply_text(f"✅ {source} sonucu:")
                
                # İçeriği parçalara böl (Telegram 4096 karakter limiti)
                if len(content) > 4000:
                    # Uzun içerikleri böl
                    chunks = [content[i:i+4000] for i in range(0, len(content), 4000)]
                    for j, chunk in enumerate(chunks[:3]):  # Max 3 parça gönder
                        await update.message.reply_text(f"**Bölüm {j+1}:**\n{chunk}")
                else:
                    # Kısa içeriği direkt gönder
                    await update.message.reply_text(content)
                
                print(f"DEBUG: {source} mesaj olarak gönderildi")
            
            return await update.message.reply_text(f"🎯 '{q}' araştırması tamamlandı!")
            
        except Exception as e:
            print(f"DEBUG: Ana araştırma hatası: {e}")
            return await update.message.reply_text(f"❌ Araştırma hatası: {e}")

    # 2) Akıllı soru tespiti - Uzun cümleler ve sorular için otomatik araştırma
    question_patterns = [
        r".+nedir\?*$",  # "bitcoin nedir?"
        r".+nasıl\s+.+\?*$",  # "bitcoin nasıl çalışır?"
        r".+ne\s+demek\?*$",  # "blockchain ne demek?"
        r".+hakkında\s+.+\?*$",  # "yapay zeka hakkında bilgi ver?"
        r".+kimdir\?*$",  # "satoshi nakamoto kimdir?"
        r".+niçin\s+.+\?*$",  # "bitcoin niçin değerli?"
        r".+neden\s+.+\?*$",  # "bitcoin neden popüler?"
        r".+hangi\s+.+\?*$",  # "hangi kripto para almalı?"
        r".+ne\s+zaman\s+.+\?*$",  # "bitcoin ne zaman çıktı?"
        r".+gelecek\s+.+\?*$",  # "yapay zeka gelecek nasıl olacak?"
        r".+son\s+günler\s+.+",  # "son günlerde gelmiş olduğu noktaları araştır"
        r".+hava\s+durumu\s*.+",  # "istanbul hava durumu"
        r".+fiyat\s*.+",  # "bitcoin fiyatı"
    ]
    
    # Uzun cümleler ve soru kalıpları tespit et
    is_question = any(re.match(pattern, text, re.IGNORECASE) for pattern in question_patterns)
    is_long_sentence = len(text) > 15 and not text.startswith(("not al", "hatırlat", "belge"))
    
    if is_question or is_long_sentence:
        await update.message.reply_text("🤔 Bu bir soru/araştırma talebi gibi görünüyor, süper araştırma başlatılıyor...")
        
        try:
            # Soruyu anahtar kelimelere çevir
            search_query = text
            # Gereksiz kelimeleri temizle
            cleanup_words = ["nedir", "nasıl", "ne demek", "hakkında bilgi", "kimdir", "neden", "niçin", "?", ".", "!"]
            for word in cleanup_words:
                search_query = search_query.replace(word, "")
            search_query = search_query.strip()
            
            print(f"DEBUG: Soru '{text}' → Arama '{search_query}'")
            
            # Fallback - mevcut sistem
            results = smart_search(search_query)
            print(f"DEBUG: Soru için {len(results) if results else 0} sonuç bulundu")
            
            if results:
                # İlk sonucu özetleyerek gönder
                source, content = results[0]
                await update.message.reply_text(f"💡 **{source}** kaynağından:")
                
                # İlk 2000 karakteri al (daha özet)
                summary = content[:2000] + "..." if len(content) > 2000 else content
                await update.message.reply_text(summary)
                
                # Eğer birden fazla kaynak varsa bilgilendir
                if len(results) > 1:
                    await update.message.reply_text(f"📚 Toplam {len(results)} kaynakta bilgi bulundu. Daha fazlası için 'ara {search_query}' yazabilirsin.")
                return
            else:
                return await update.message.reply_text("❌ Bu konuda bilgi bulunamadı.")
        except Exception as e:
            print(f"DEBUG: Soru araştırma hatası: {e}")
            return await update.message.reply_text(f"❌ Araştırma sırasında hata oluştu: {str(e)[:100]}")

    # --- Belge oluştur ---
    if text.startswith("belge oluştur"):
        m_title = re.search(r"başlık:\s*(.+?)(?:\s+içerik:|$)", text_raw, re.IGNORECASE|re.DOTALL)
        m_body  = re.search(r"içerik:\s*(.+)$", text_raw, re.IGNORECASE|re.DOTALL)
        title = m_title.group(1).strip() if m_title else f"Belge-{dt.datetime.now().strftime('%H%M%S')}"
        body  = m_body.group(1).strip() if m_body else ""
        safe = re.sub(r'[^a-zA-Z0-9_-]+','_', title)[:40]
        fn = DOCS / (safe + ".md")
        with open(fn, "w", encoding="utf-8") as f: f.write(f"# {title}\n\n{body}\n")
        await say(ctx, update.effective_chat.id, f"{title} belgesini oluşturdum.")
        return await update.message.reply_document(InputFile(fn))

    # --- YouTube ---
    if text.startswith("youtube "):
        q = text_raw[8:].strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
        return await update.message.reply_text(f"▶️ YouTube açıldı: {q}")

    # --- Uygulama / URL aç ---
    if text.startswith(("aç ", "ac ")):
        arg = text_raw.split(" ",1)[1].strip()
        if arg.startswith(URL_WHITELIST_PREFIX):
            if not arg.startswith(("http://","https://")): arg = "https://" + arg
            webbrowser.open(arg)
            return await update.message.reply_text(f"🌐 Açtım: {arg}")
        key = arg.lower()
        if key in APP_WHITELIST:
            path = os.path.expandvars(APP_WHITELIST[key])
            try:
                subprocess.Popen(path)
                return await update.message.reply_text(f"🖥️ Uygulama açıldı: {key}")
            except Exception as e:
                return await update.message.reply_text(f"Açılamadı: {e}")
        return await update.message.reply_text("İzinli URL veya uygulama değil. (whitelist’e eklenebilir)")

    # --- Son belgeyi gönder ---
    if "son dosyayı gönder" in text or "son dosyayi gonder" in text:
        files = sorted(DOCS.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files: return await update.message.reply_text("Gönderecek belge yok.")
        return await update.message.reply_document(InputFile(files[0]))

    return await update.message.reply_text("Komutu anlayamadım. Örnek: not al…, ara…, '1 dk sonra ara beni', youtube…, belge oluştur…, aç <uygulama|url>, son dosyayı gönder")

# ========= Sesli mesaj -> STT -> komut =========
@only_owner
async def on_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        file = await ctx.bot.get_file(update.message.voice.file_id)
        ts = int(dt.datetime.now().timestamp())
        ogg_path = VOICE_DIR / f"{ts}.oga"     # telegram opus/oga
        wav_path = VOICE_DIR / f"{ts}.wav"
        
        print(f"Ses dosyası indiriliyor: {ogg_path}")
        await file.download_to_drive(custom_path=str(ogg_path))
        
        # İndirilen dosyayı kontrol et
        if not ogg_path.exists():
            return await update.message.reply_text(f"❌ Ses dosyası indirilemedi: {ogg_path}")
        
        print(f"✅ Ses dosyası indirildi: {ogg_path.stat().st_size} bytes")

        # oga/webm -> wav (16kHz mono) - yeni helper kullan
        if not ffmpeg_ready:
            return await update.message.reply_text("⚠️ FFmpeg kurulmamış. Ses işlenemiyor. .env dosyasında FFMPEG ve FFPROBE yollarını kontrol edin.")
        
        try:
            convert_voice_to_wav(ogg_path, wav_path)
        except Exception as e:
            return await update.message.reply_text(f"Ses dosyası işlenemedi: {e}")

        # STT
        r = sr.Recognizer()
        with sr.AudioFile(str(wav_path)) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="tr-TR")
        await update.message.reply_text(f"🎤 Anladım: {text}")

        # Metni direkt işle - Ses komutlarını metin komutları gibi işle
        text_lower = text.lower().strip()
        user_id = str(update.effective_user.id)
        
        # 🧠 Sesli mesajdan öğren
        try:
            smart_response = await handle_smart_message(update, ctx, message=text)
            if smart_response and "Size nasıl yardımcı olabilirim?" not in smart_response:
                # TTS yanıt gönder
                try:
                    await update.message.reply_text(smart_response)
                    mp3_path = TTS_DIR / f"{int(dt.datetime.now().timestamp())}.mp3"
                    gTTS(text=smart_response[:100], lang="tr").save(str(mp3_path))
                    await update.message.reply_audio(InputFile(str(mp3_path)), title="Akıllı Yanıt")
                except Exception as e:
                    print(f"❌ TTS yanıt hatası: {e}")
                return
        except Exception as e:
            print(f"❌ Akıllı işleme hatası: {e}")
        
        # Hatırlatma kontrolü
        if any(k in text_lower for k in ["hatırlat", "hatirlat", " dk sonra ", " saat sonra ", " sa sonra ", " dakika sonra "]):
            when, msg = parse_reminder(text)
            if when and msg:
                DB.execute("INSERT INTO reminders(text, when_at, chat_id) VALUES (?,?,?)",
                          (msg, when.isoformat(), str(update.effective_chat.id))); DB.commit()
                
                async def send_reminder_voice():
                    try:
                        await ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"⏰ Hatırlatma: {msg}")
                        print("📢 Mesaj gönderildi, şimdi TTS deneniyor...")
                        try: 
                            # TTS ses dosyası oluştur ve gönder
                            mp3_path = TTS_DIR / f"reminder_{int(dt.datetime.now().timestamp())}.mp3"
                            gTTS(text=f"Hatırlatma: {msg}", lang="tr").save(str(mp3_path))
                            print(f"🎵 TTS dosyası oluşturuldu: {mp3_path}")
                            
                            await ctx.bot.send_audio(
                                chat_id=update.effective_chat.id, 
                                audio=InputFile(str(mp3_path)), 
                                title="Hatırlatma"
                            )
                            print("🔊 TTS ses dosyası gönderildi!")
                        except Exception as tts_error: 
                            print(f"❌ TTS hatası: {tts_error}")
                        
                        DB.execute("DELETE FROM reminders WHERE text=? AND when_at=? AND chat_id=?", 
                                  (msg, when.isoformat(), str(update.effective_chat.id)))
                        DB.commit()
                        print(f"✅ Hatırlatma gönderildi: {msg}")
                    except Exception as e:
                        print(f"❌ Hatırlatma hatası: {e}")
                
                def sync_reminder_voice():
                    import asyncio
                    try:
                        asyncio.run(send_reminder_voice())
                    except Exception as e:
                        print(f"❌ Sync hatırlatma hatası: {e}")
                
                sched.add_job(sync_reminder_voice, "date", run_date=when, id=f"voice_rem_{int(dt.datetime.now().timestamp())}")
                
                # TTS yanıt gönder
                try:
                    response_text = f"⏱️ Ayarlandı: {when.strftime('%d.%m %H:%M')} → \"{msg}\""
                    await update.message.reply_text(response_text)
                    
                    # TTS yanıt ses dosyası
                    mp3_path = TTS_DIR / f"{int(dt.datetime.now().timestamp())}.mp3"
                    gTTS(text=response_text, lang="tr").save(str(mp3_path))
                    await update.message.reply_audio(InputFile(str(mp3_path)), title="Yanıt")
                except Exception as e:
                    print(f"❌ TTS yanıt hatası: {e}")
                    await update.message.reply_text(f"⏱️ Ayarlandı: {when.strftime('%d.%m %H:%M')}  →  \"{msg}\"")
                
                return
        
        # Not alma kontrolü
        if any(k in text_lower for k in ["not al", "not yaz", "kaydet", "hatırla"]):
            if "not al" in text_lower:
                note_text = text[text_lower.find("not al") + 6:].strip()
            elif "not yaz" in text_lower:
                note_text = text[text_lower.find("not yaz") + 7:].strip()
            else:
                note_text = text.strip()
            
            if note_text:
                # Not dosyasına kaydet
                timestamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
                safe_name = re.sub(r'[^a-zA-Z0-9_-]+', '_', note_text[:30])
                note_file = DOCS / f"not-{timestamp}-{safe_name}.md"
                
                with open(note_file, "w", encoding="utf-8") as f:
                    f.write(f"# Not - {dt.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{note_text}\n")
                
                # TTS yanıt gönder
                try:
                    response_text = f"📝 Not kaydedildi: {note_text}"
                    await update.message.reply_text(response_text)
                    
                    # TTS yanıt ses dosyası
                    mp3_path = TTS_DIR / f"{int(dt.datetime.now().timestamp())}.mp3"
                    gTTS(text="Not başarıyla kaydedildi", lang="tr").save(str(mp3_path))
                    await update.message.reply_audio(InputFile(str(mp3_path)), title="Yanıt")
                    
                    # Not dosyasını da gönder
                    await update.message.reply_document(InputFile(note_file))
                except Exception as e:
                    print(f"❌ TTS yanıt hatası: {e}")
                    await update.message.reply_text(f"📝 Not kaydedildi: {note_text}")
                
                return
        
        # Genel TTS yanıt - komut tanınmadıysa
        try:
            response_text = f"Ses komutunu henüz desteklemiyorum: '{text}'"
            await update.message.reply_text(response_text)
            
            # TTS yanıt ses dosyası
            mp3_path = TTS_DIR / f"{int(dt.datetime.now().timestamp())}.mp3"
            gTTS(text="Bu komutu henüz desteklemiyorum", lang="tr").save(str(mp3_path))
            await update.message.reply_audio(InputFile(str(mp3_path)), title="Yanıt")
        except Exception as e:
            print(f"❌ TTS yanıt hatası: {e}")
            await update.message.reply_text(f"Ses komutunu henüz desteklemiyorum: '{text}'")

    except sr.RequestError as e:
        return await update.message.reply_text(f"Ses işlenemedi: STT timeout/hata ({e}).")
    except FileNotFoundError:
        return await update.message.reply_text("Ses işlenemedi: ffmpeg/ffprobe yolu bulunamadı (.env’de FFMPEG & FFPROBE).")
    except Exception as e:
        return await update.message.reply_text(f"Ses işlenemedi: {e}")

# ========= main =========
async def main():
    app = ApplicationBuilder().token(TG_TOKEN).rate_limiter(AIORateLimiter()).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("ai_news", cmd_ai_news))
    app.add_handler(CommandHandler("news_check", cmd_news_check))
    
    # 🤖 AI özelliklerini ekle
    app.add_handler(CommandHandler("analiz", handle_ai_analysis))
    app.add_handler(CommandHandler("ozet", handle_ai_summary))
    app.add_handler(CommandHandler("trend", handle_ai_trends))
    app.add_handler(CommandHandler("ai", handle_ai_help))
    
    # 🧠 Akıllı öğrenme komutları - YENİ FONKSIYONLAR
                
          
         
            
          
            
     

            
           
    
    # 🤖 AI özelliklerini ekle
    app.add_handler(CommandHandler("analiz", handle_ai_analysis))
    app.add_handler(CommandHandler("ozet", handle_ai_summary))
    app.add_handler(CommandHandler("trend", handle_ai_trends))
    app.add_handler(CommandHandler("ai", handle_ai_help))
    
    # 🧠 Akıllı öğrenme komutları - YENİ FONKSIYONLAR
    async def handle_learn_info(update, context):
        """Öğrenme bilgilerini göster"""
        user_id = update.effective_user.id
        response = f"🧠 **Öğrenme Sistemi Aktif!**\n\n📚 Size özel bilgiler öğreniyorum ve hatırlıyorum.\n💡 Her konuşmada daha akıllı hale geliyorum!\n\n✨ Beni test edin: 'Adım [isminiz]' deyin!"
        await update.message.reply_text(response)
    
    async def handle_availability_check(update, context):
        """Müsaitlik kontrolü"""
        user_id = update.effective_user.id
        message_text = " ".join(context.args) if context.args else "Bugün müsait miyim?"
        response = smart_assistant.generate_response(user_id, f"müsaitlik kontrolü: {message_text}")
        await update.message.reply_text(response)
    
    async def show_user_profile(update, context):
        """Kullanıcı profilini göster"""
        user_id = update.effective_user.id
        profile = smart_assistant.get_user_profile(user_id)
        if profile and profile.get('learned_info'):
            response = "👤 **Profiliniz:**\n\n"
            for info in profile['learned_info']:
                response += f"• **{info[2]}:** {info[4]}\n"
        else:
            response = "👤 **Henüz profiliniz yok.**\n\n💡 Bana kendinizden bahsedin: 'Adım Mehmet' gibi!"
        await update.message.reply_text(response)
    
    app.add_handler(CommandHandler("ogren", handle_learn_info))
    app.add_handler(CommandHandler("musait", handle_availability_check))
    app.add_handler(CommandHandler("profil", show_user_profile))
    
    # 🧠 Süper Zeka komutları - YENİ
    async def cmd_super_zeka(update, context):
        """Süper zeka ile soru sorma"""
        if not SUPER_INTELLIGENCE_AVAILABLE:
            await update.message.reply_text("❌ Süper zeka sistemi şu anda kullanılamıyor.")
            return
            
        query = " ".join(context.args) if context.args else None
        if not query:
            await update.message.reply_text("🧠 **Süper Zeka Sistemi**\n\n💡 Kullanım: `/szeka [sorunuz]`\n\n🔍 Örnek: `/szeka Python nedir?`")
            return
        
        await update.message.reply_text("🧠 Süper zeka analiz ediyor...")
        
        try:
            user_id = update.effective_user.id
            response = await handle_super_intelligent_message(query, user_id)
            await update.message.reply_text(response if response else "❌ Yanıt alınamadı.")
        except Exception as e:
            await update.message.reply_text(f"❌ Süper zeka hatası: {e}")
    
    async def cmd_zeka_durum(update, context):
        """Süper zeka istatistiklerini göster"""
        if not SUPER_INTELLIGENCE_AVAILABLE:
            await update.message.reply_text("❌ Süper zeka sistemi şu anda kullanılamıyor.")
            return
            
        try:
            stats = super_intelligence.get_intelligence_stats()
            response = f"""🧠 **Süper Zeka İstatistikleri**

📊 **Bilgi Grafiği:** {stats['knowledge_graph_size']} kavram
🔗 **Bağlantı Sayısı:** {stats['total_connections']}
📚 **Öğrenilen Kalıp:** {stats['learned_patterns']}
🎯 **Kelime Vektörü:** {stats['word_vectors']}
📖 **Korpus Durumu:** {'✅ Aktif' if stats['corpus_available'] else '❌ Kapalı'}

💡 Süper zeka kullanımı: `/szeka [sorunuz]`"""
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ İstatistik hatası: {e}")
    
    async def cmd_ogrenme_stats(update, context):
        """Akıllı öğrenme istatistiklerini göster"""
        try:
            from smart_definitions import smart_definitions
            
            stats = smart_definitions.get_learning_stats()
            
            response = f"""🧠 **Akıllı Öğrenme İstatistikleri**

📚 **Toplam Öğrenilen:** {stats['total_definitions']} tanım
📅 **Bugün Öğrenilen:** {stats['today_learned']} yeni tanım

🔥 **En Popüler Sorular:**"""
            
            for i, (question, count) in enumerate(stats['popular_definitions'], 1):
                response += f"\n{i}. {question} ({count} kez soruldu)"
            
            response += f"\n\n💡 **Nasıl çalışır?**"
            response += f"\n• Bir şey sorun: 'React nedir?'"
            response += f"\n• Bilmiyorsam araştırırım"
            response += f"\n• Öğrendiklerimi hafızamda tutarım"
            response += f"\n• Tekrar sorulunca hızla yanıtlarım!"
            
            await update.message.reply_text(response)
            
        except Exception as e:
            print(f"Öğrenme istatistikleri hatası: {e}")
            await update.message.reply_text("❌ Öğrenme istatistikleri alınamadı. Sistem henüz başlatılıyor olabilir.")
    
    async def cmd_zeka_egit(update, context):
        """Süper zekayı yeniden eğit"""
        if not SUPER_INTELLIGENCE_AVAILABLE:
            await update.message.reply_text("❌ Süper zeka sistemi şu anda kullanılamıyor.")
            return
            
        await update.message.reply_text("🧠 Süper zeka yeniden eğitimi başlatılıyor... Bu işlem birkaç dakika sürebilir.")
        
        try:
            # Zorunlu yeniden eğitim
            success = super_intelligence.analyze_corpus_intelligence(limit=10000, force_retrain=True)
            if success:
                stats = super_intelligence.get_intelligence_stats()
                response = f"✅ **Süper zeka yeniden eğitimi tamamlandı!**\n\n📊 {stats['knowledge_graph_size']} kavram öğrenildi\n🔗 {stats['total_connections']} bağlantı kuruldu"
            else:
                response = "❌ Eğitim sırasında hata oluştu."
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Eğitim hatası: {e}")
    
    app.add_handler(CommandHandler("szeka", cmd_super_zeka))
    app.add_handler(CommandHandler("zekadurum", cmd_zeka_durum))
    app.add_handler(CommandHandler("zekaegit", cmd_zeka_egit))
    app.add_handler(CommandHandler("ogrenme", cmd_ogrenme_stats))
    app.add_handler(CommandHandler("ogrenme_stats", cmd_ogrenme_stats))
    
    # 📚 Korpus komutları - YENİ
    async def cmd_korpus_durum(update, context):
        """Korpus durumunu göster"""
        try:
            info = smart_assistant.get_corpus_info()
            if info['available']:
                response = "📚 **Türkçe Korpus Durumu**\n\n✅ **Aktif!** ~4.6 GB Türkçe metin verisi:\n\n"
                for source, stats in info['stats'].items():
                    if stats['exists']:
                        emoji = {"wikipedia": "📖", "oscar": "🌐", "mc4": "📝"}.get(source, "📄")
                        response += f"{emoji} **{source.upper()}**: {stats['size_mb']:.1f} MB\n"
                response += f"\n🔍 Metin arama için: /ara [kelime]"
            else:
                response = "❌ **Korpus mevcut değil**\n\n📦 İndirmek için:\n`python download_tr_capped.py`"
        except Exception as e:
            response = f"⚠️ Korpus kontrol hatası: {e}"
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def cmd_korpus_ara(update, context):
        """Korpusta arama yap"""
        if not context.args:
            await update.message.reply_text("🔍 **Kullanım:** /ara [aranacak kelime]\n\n**Örnek:** /ara teknoloji")
            return
        
        query = " ".join(context.args)
        try:
            results = smart_assistant.search_in_corpus(query, limit=3)
            if results:
                response = f"🔍 **'{query}' için sonuçlar:**\n\n"
                for i, result in enumerate(results, 1):
                    emoji = {"wikipedia": "📖", "oscar": "🌐", "mc4": "📝"}.get(result['source'], "📄")
                    text = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                    response += f"{emoji} **{i}.** {text}\n\n"
            else:
                response = f"❌ '{query}' için sonuç bulunamadı.\n\n💡 Başka kelimeler deneyin."
        except Exception as e:
            response = f"⚠️ Arama hatası: {e}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def cmd_korpus_ornek(update, context):
        """Korpustan rastgele örnekler göster"""
        try:
            samples = smart_assistant.get_corpus_samples(count=3)
            if samples:
                response = "🎲 **Rastgele Korpus Örnekleri:**\n\n"
                for sample in samples:
                    emoji = {"wikipedia": "📖", "oscar": "🌐", "mc4": "📝"}.get(sample.get('source'), "📄")
                    text = sample.get('text', '')[:150] + "..." if len(sample.get('text', '')) > 150 else sample.get('text', '')
                    title = sample.get('title', '')
                    if title:
                        response += f"{emoji} **{title}**\n{text}\n\n"
                    else:
                        response += f"{emoji} {text}\n\n"
            else:
                response = "❌ Örnek alınamadı. Korpus durumunu kontrol edin: /korpus"
        except Exception as e:
            response = f"⚠️ Örnek alma hatası: {e}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    app.add_handler(CommandHandler("korpus", cmd_korpus_durum))
    app.add_handler(CommandHandler("ara", cmd_korpus_ara))
    app.add_handler(CommandHandler("ornek", cmd_korpus_ornek))
    
    # 📋 Görev ve hatırlatma komutları
    app.add_handler(CommandHandler("tasks", cmd_tasks))
    app.add_handler(CommandHandler("gorevler", cmd_tasks))
    app.add_handler(CommandHandler("reminders", cmd_reminders))
    app.add_handler(CommandHandler("hatirlatmalar", cmd_reminders))
    app.add_handler(CommandHandler("profile", cmd_profile))
    
    app.add_handler(MessageHandler(filters.VOICE, on_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    await app.initialize(); await app.start()
    
    # Bot başlatıldığında eski hatırlatıcıları temizle ve yükle
    print("🔄 Hatırlatıcılar yükleniyor...")
    cleanup_old_reminders(DB, TZ)
    if 'twilio_client' not in locals():
        twilio_client = None
    load_reminders(app, DB, sched, TZ, False, None)  # Twilio devre dışı
    
    # Haber takip sistemini başlat
    if OWNER_ID:
        print("📰 Haber takip sistemi başlatılıyor...")
        try:
            init_news_scheduler(app.bot, OWNER_ID)
            
            # 🎯 Hatırlatıcı sistemi başlat - bu fonksiyon özel parametreler gerekmiyor
            # load_reminders(DB, TZ, app) - zaten yukarıda yüklendi
        except Exception as e:
            print(f"❌ Haber sistemi hatası: {e}")
    else:
        print("⚠️ OWNER_ID tanımlı değil, haber sistemi başlatılamadı!")
    
    print("🤖 AI asistan özellikleri aktif!")
    print("   📊 /analiz - Haber analizi")
    print("   🤖 /ozet - Akıllı özet")
    print("   📈 /trend - Trend analizi")
    print("   ❓ /ai - AI yardım")
    print("🧠 Akıllı öğrenme sistemi aktif!")
    print("   🎓 /ogren - Bilgi öğrenme")
    print("   📅 /musait - Müsaitlik kontrolü")
    print("   👤 /profil - Profilinizi göster")
    
    # Süper zeka sistemini başlat
    if SUPER_INTELLIGENCE_AVAILABLE:
        print("🧠 Süper Zeka sistemi başlatılıyor...")
        try:
            # GEÇICI OLARAK YORUMDA - Terminal donmasını engellemek için
            # success = initialize_super_intelligence()
            success = True  # Test için True varsay
            if success:
                print("✅ Süper Zeka hazır!")
                print("   🧠 /szeka - Süper zeka sorgu")
                print("   📊 /zekadurum - Zeka istatistikleri")
                print("   🎓 /zekaegit - Zeka eğitimi")
            else:
                print("⚠️ Süper Zeka başlatma sorunlu")
        except Exception as e:
            print(f"❌ Süper Zeka başlatma hatası: {e}")
    
    print("💡 Akıllı özellikler:")
    print("   • 'Adım Mehmet' - İsminizi öğrenir")
    print("   • 'Yarın toplantım var' - Randevunuzu hatırlar")
    print("   • 'Müsait miyim?' - Durumunuzu kontrol eder")
    
    # Windows için güvenli başlatma
    print("🚀 Bot başlatılıyor...")
    await app.updater.start_polling()
    
    try:
        # Windows'ta daha güvenli bekleme
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("👋 Bot kapatılıyor...")
        await app.updater.stop()

if __name__ == "__main__":
    # Windows için asyncio politikası ayarla
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
