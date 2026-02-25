"""
Hatırlatıcı yükleme ve yönetimi için yardımcı fonksiyonlar
"""
import os
import sqlite3
import datetime as dt
from zoneinfo import ZoneInfo
from apscheduler.jobstores.base import ConflictingIdError
import requests

def load_reminders(app, db, scheduler, tz, twilio_ok=False, twilio_client=None):
    """Bot başlatıldığında veritabanındaki gelecekteki hatırlatıcıları scheduler'a yükler"""
    cursor = db.execute("SELECT id, text, when_at, chat_id FROM reminders")
    loaded_count = 0
    
    for row in cursor.fetchall():
        reminder_id, text, when_str, chat_id = row
        try:
            when = dt.datetime.fromisoformat(when_str)
            now = dt.datetime.now(ZoneInfo(tz))
            
            # Eğer hatırlatma zamanı geçmişte ise, veritabanından sil
            if when <= now:
                db.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
                db.commit()
                print(f"Geçmiş hatırlatıcı silindi: {text}")
                continue
                
            async def send_reminder(reminder_text=text, chat_id=int(chat_id), rid=reminder_id):
                try:
                    await app.bot.send_message(chat_id=chat_id, text=f"⏰ Hatırlatma: {reminder_text}")
                    
                    # TTS ses gönderme (opsiyonel)
                    try: 
                        from gtts import gTTS
                        import pathlib
                        tts_dir = pathlib.Path(__file__).parent / "data" / "tts"
                        mp3_path = tts_dir / f"reminder_{int(dt.datetime.now().timestamp())}.mp3"
                        gTTS(text=f"Hatırlatma: {reminder_text}", lang="tr").save(str(mp3_path))
                        from telegram import InputFile
                        await app.bot.send_audio(chat_id=chat_id, audio=InputFile(mp3_path), title="Hatırlatma")
                    except Exception as e:
                        print(f"TTS hatası: {e}")
                    
                    # Twilio arama (opsiyonel)
                    if twilio_ok and twilio_client:
                        try:
                            twilio_client.calls.create(
                                to=os.getenv("TWILIO_TO"), 
                                from_=os.getenv("TWILIO_FROM"),
                                url=f'http://twimlets.com/message?Message%5B0%5D={requests.utils.quote("Hatırlatma: " + reminder_text)}'
                            )
                        except Exception as e:
                            print(f"Twilio arama hatası: {e}")
                    
                    # Hatırlatma gönderildikten sonra veritabanından sil
                    db.execute("DELETE FROM reminders WHERE id=?", (rid,))
                    db.commit()
                    print(f"Hatırlatıcı gönderildi ve silindi: {reminder_text}")
                    
                except Exception as e:
                    print(f"Hatırlatıcı gönderim hatası (ID: {rid}): {e}")
            
            try:
                scheduler.add_job(
                    lambda rt=text, cid=int(chat_id), rid=reminder_id: app.create_task(send_reminder(rt, cid, rid)),
                    "date", 
                    run_date=when, 
                    id=f"rem_{reminder_id}"
                )
                loaded_count += 1
                print(f"Hatırlatıcı yüklendi: {when.strftime('%d.%m %H:%M')} - {text}")
            except ConflictingIdError:
                print(f"Hatırlatıcı zaten var: rem_{reminder_id}")
        except Exception as e:
            print(f"Hatırlatıcı yüklenirken hata (ID: {reminder_id}): {e}")
    
    print(f"Toplam {loaded_count} hatırlatıcı yüklendi.")
    return loaded_count

def cleanup_old_reminders(db, tz):
    """Geçmiş hatırlatıcıları temizle"""
    now = dt.datetime.now(ZoneInfo(tz))
    cursor = db.execute("SELECT id, text, when_at FROM reminders")
    cleaned = 0
    
    for row in cursor.fetchall():
        reminder_id, text, when_str = row
        try:
            when = dt.datetime.fromisoformat(when_str)
            if when <= now:
                db.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
                cleaned += 1
        except Exception:
            # Hatalı tarih formatı varsa da sil
            db.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
            cleaned += 1
    
    if cleaned > 0:
        db.commit()
        print(f"{cleaned} geçmiş hatırlatıcı temizlendi.")
    
    return cleaned
