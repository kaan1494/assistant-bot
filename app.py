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
    from smart_assistant_fixed import smart_assistant, handle_smart_message, handle_availability_check, handle_learn_info, show_user_profile
    from web_research import search_web_smart
    from task_reminder import create_task_reminder, get_user_task_list, get_user_reminders
    AI_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI features loading error: {e}")
    AI_FEATURES_AVAILABLE = False

# --- SES / TTS / STT
from gtts import gTTS
from pydub import AudioSegment
from pydub.utils import which
import speech_recognition as sr

# --- (opsiyonel) telefonla arama (Twilio)
try:
    from twilio.rest import Client as TwilioClient
except Exception:
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
if ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + ffmpeg_dir
    print(f"FFmpeg PATH'e eklendi: {ffmpeg_dir}")

DB = sqlite3.connect(DATA / "assistant.db", check_same_thread=False)
DB.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, title TEXT, body TEXT, created_at TEXT)")
DB.execute("CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY, text TEXT, when_at TEXT, chat_id TEXT)")
DB.commit()

TZ = os.getenv("TZ", "Europe/Istanbul")
sched = BackgroundScheduler(timezone=TZ); sched.start()

TG_TOKEN = os.getenv("TG_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

# FFmpeg kurulumunu kontrol et
ffmpeg_ready = setup_ffmpeg()

# Twilio opsiyonel
twilio_ok = False
if TwilioClient:
    TWILIO_SID=os.getenv("TWILIO_SID"); TWILIO_TOKEN=os.getenv("TWILIO_TOKEN")
    TWILIO_FROM=os.getenv("TWILIO_FROM"); TWILIO_TO=os.getenv("TWILIO_TO")
    if all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TWILIO_TO]):
        twilio_client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
        twilio_ok = True
    else:
        twilio_client = None

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
        "🤖 **Akıllı Asistan Hazır!**\n\n"
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
        "🎤 **Ses:** Sesli mesaj gönderirsen yazıya çevirip komut gibi işlerim.\n"
        "🤖 **Akıllı:** Soru sorarsan otomatik araştırırım!"
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
        DB.execute("INSERT INTO reminders(text, when_at, chat_id) VALUES (?,?,?)",
                   (msg, when.isoformat(), str(update.effective_chat.id))); DB.commit()

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
                    if twilio_ok:
                        twilio_client.calls.create(
                            to=os.getenv("TWILIO_TO"), from_=os.getenv("TWILIO_FROM"),
                            url=f'http://twimlets.com/message?Message%5B0%5D={requests.utils.quote("Hatırlatma: " + msg)}'
                        )
                    # Hatırlatma gönderildikten sonra veritabanından sil
                    DB.execute("DELETE FROM reminders WHERE text=? AND when_at=? AND chat_id=?", 
                              (msg, when.isoformat(), str(update.effective_chat.id)))
                    DB.commit()
                    print(f"✅ Hatırlatma gönderildi: {msg}")
                except Exception as e:
                    print(f"❌ Hatırlatma hatası: {e}")
            
            # Yeni event loop oluştur ve çalıştır
            try:
                asyncio.run(send_it())
            except Exception as e:
                print(f"❌ Sync hatırlatma hatası: {e}")

        sched.add_job(sync_reminder, "date", run_date=when, id=f"rem_{int(dt.datetime.now().timestamp())}")
        return await update.message.reply_text(f"⏱️ Ayarlandı: {when.strftime('%d.%m %H:%M')}  →  '{msg}'")
        return await update.message.reply_text(f"⏱️ Ayarlandı: {when.strftime('%d.%m %H:%M')}  →  “{msg}”")

    # 🧠 Akıllı öğrenme ve hatırlama özelliği - TÜM MESAJLAR İÇİN
    try:
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
            learn_response = await handle_learn_info(update, ctx)
            await update.message.reply_text(learn_response)
            return
        except Exception as e:
            print(f"❌ Bilgi öğrenme hatası: {e}")
    
    # Müsaitlik kontrolü
    if "müsait miyim" in text.lower() or "boş muyum" in text.lower():
        availability_response = await handle_availability_check(update, ctx)
        await update.message.reply_text(availability_response)
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
            if AI_FEATURES_AVAILABLE:
                web_results = search_web_smart(q)
                
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
            
            # SÜPER WEB RESEARCH FIRST!
            if AI_FEATURES_AVAILABLE:
                web_results = search_web_smart(text)  # Orijinal metni kullan
                
                if web_results:
                    best_result = web_results[0]
                    
                    response = f"""💡 **{best_result['title']}**

{best_result['content']}

🌐 **Kaynak:** {best_result['source']}
"""
                    
                    if best_result.get('url'):
                        response += f"🔗 **Detaylı Bilgi:** {best_result['url']}\n"
                    
                    await update.message.reply_text(response)
                    
                    # Ek sonuçlar varsa bilgilendir
                    if len(web_results) > 1:
                        await update.message.reply_text(f"📚 Toplam {len(web_results)} kaynakta bilgi bulundu. Daha fazlası için 'ara {search_query}' yazabilirsin.")
                    
                    return
            
            # Fallback - mevcut sistem
            results = smart_search(search_query)
            print(f"DEBUG: Soru için {len(results)} sonuç bulundu")
            
            if not results:
                return await update.message.reply_text("❌ Bu konuda bilgi bulunamadı.")
            
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
            
        except Exception as e:
            print(f"DEBUG: Soru araştırma hatası: {e}")
            # Normal mesaj işleme devam et
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
    load_reminders(app, DB, sched, TZ, twilio_ok, twilio_client)
    
    # Haber takip sistemini başlat
    if OWNER_ID:
        print("📰 Haber takip sistemi başlatılıyor...")
        init_news_scheduler(app.bot, OWNER_ID)
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
    print("💡 Akıllı özellikler:")
    print("   • 'Adım Mehmet' - İsminizi öğrenir")
    print("   • 'Yarın toplantım var' - Randevunuzu hatırlar")
    print("   • 'Müsait miyim?' - Durumunuzu kontrol eder")
    
    await app.updater.start_polling()
    import asyncio; await asyncio.Event().wait()

if __name__ == "__main__":
    import asyncio; asyncio.run(main())
