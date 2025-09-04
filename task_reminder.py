"""
🕐 SÜPER AKI TASK REMINDER SYSTEM
Akıllı görev ve hatırlatma sistemi
"""

import sqlite3
import datetime
import re
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import logging

logging.basicConfig(level=logging.INFO)

class TaskReminderSystem:
    """Süper akıllı görev ve hatırlatma sistemi"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.init_reminder_db()
        
    def init_reminder_db(self):
        """Hatırlatma veritabanını başlat"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Hatırlatma tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    reminder_text TEXT,
                    reminder_time TIMESTAMP,
                    original_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_sent BOOLEAN DEFAULT FALSE,
                    bot_message_id INTEGER
                )
            """)
            
            # Görev tablosu 
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task_text TEXT,
                    due_date TIMESTAMP,
                    priority TEXT DEFAULT 'medium',
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Reminder DB hatası: {e}")
    
    def parse_task_message(self, message):
        """Mesajdan görev ve zamanı çıkar"""
        try:
            message_lower = message.lower()
            
            # Tarih/saat pattern'leri
            time_patterns = [
                r'(\d{1,2}):(\d{2})\s*da',  # 20:00 da, 19:00 da
                r'(\d{1,2})\s*da',          # 20 da, 8 da  
                r'saat\s*(\d{1,2})',       # saat 20
                r'(\d{1,2})\s*gibi',       # 8 gibi
                r'akşam\s*(\d{1,2})',      # akşam 8
                r'sabah\s*(\d{1,2})',      # sabah 8
            ]
            
            # Günlük ifadeler
            day_patterns = [
                r'bugün',
                r'yarın', 
                r'öbür\s*gün',
                r'cumartesi', r'pazar', r'pazartesi', r'salı', r'çarşamba', r'perşembe', r'cuma'
            ]
            
            # Görev ifadeleri
            task_indicators = [
                'toplantı', 'randevu', 'buluşma', 'ders', 'sınav', 'iş', 'görev',
                'hatırlat', 'not et', 'kaydet', 'unutma', 'önemli', 'alarm'
            ]
            
            # Zaman çıkarma
            extracted_time = None
            for pattern in time_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    if ':' in pattern:  # Saat:dakika formatı
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                    else:  # Sadece saat
                        hour = int(match.group(1))
                        minute = 0
                    
                    # 24 saat formatına çevir
                    if hour < 24:
                        extracted_time = {'hour': hour, 'minute': minute}
                        break
            
            # Gün çıkarma
            extracted_day = None
            today = datetime.datetime.now()
            
            if 'bugün' in message_lower:
                extracted_day = today.date()
            elif 'yarın' in message_lower:
                extracted_day = (today + datetime.timedelta(days=1)).date()
            elif 'öbür gün' in message_lower or 'öbürgün' in message_lower:
                extracted_day = (today + datetime.timedelta(days=2)).date()
            
            # Haftanın günleri
            weekdays = {
                'pazartesi': 0, 'salı': 1, 'çarşamba': 2, 'perşembe': 3,
                'cuma': 4, 'cumartesi': 5, 'pazar': 6
            }
            
            for day_name, day_num in weekdays.items():
                if day_name in message_lower:
                    days_ahead = day_num - today.weekday()
                    if days_ahead <= 0:  # Geçmişse gelecek haftaya
                        days_ahead += 7
                    extracted_day = (today + datetime.timedelta(days=days_ahead)).date()
                    break
            
            # Görev türü belirleme
            task_type = 'general'
            if any(word in message_lower for word in ['toplantı', 'meeting']):
                task_type = 'meeting'
            elif any(word in message_lower for word in ['randevu', 'appointment']):
                task_type = 'appointment'
            elif any(word in message_lower for word in ['ders', 'sınav', 'exam']):
                task_type = 'study'
            
            # Sonuç döndür
            if extracted_time or extracted_day:
                return {
                    'has_time': bool(extracted_time),
                    'has_date': bool(extracted_day),
                    'time': extracted_time,
                    'date': extracted_day,
                    'task_type': task_type,
                    'original_message': message,
                    'confidence': 0.8 if extracted_time and extracted_day else 0.6
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Görev parse hatası: {e}")
            return None
    
    def create_reminder(self, user_id, message, send_callback):
        """Hatırlatma oluştur"""
        try:
            parsed = self.parse_task_message(message)
            
            if not parsed:
                return None
            
            # Tarih/saat hesapla
            reminder_datetime = None
            today = datetime.datetime.now()
            
            if parsed['has_date'] and parsed['has_time']:
                # Tam tarih ve saat
                reminder_datetime = datetime.datetime.combine(
                    parsed['date'],
                    datetime.time(parsed['time']['hour'], parsed['time']['minute'])
                )
            elif parsed['has_time']:
                # Sadece saat (bugün için)
                reminder_datetime = datetime.datetime.combine(
                    today.date(),
                    datetime.time(parsed['time']['hour'], parsed['time']['minute'])
                )
                # Geçmişse yarına ertele
                if reminder_datetime <= today:
                    reminder_datetime += datetime.timedelta(days=1)
            elif parsed['has_date']:
                # Sadece tarih (09:00 varsayılan)
                reminder_datetime = datetime.datetime.combine(
                    parsed['date'],
                    datetime.time(9, 0)
                )
            
            if not reminder_datetime:
                return None
            
            # Hatırlatma zamanı (1 saat önce veya kullanıcının isteği)
            reminder_time = reminder_datetime
            
            # Eğer mesajda "x saat/dakika önce" ifadesi varsa
            if 'önce' in message.lower():
                # Pattern: "1 saat önce", "30 dakika önce"
                before_match = re.search(r'(\d+)\s*(saat|dakika)\s*önce', message.lower())
                if before_match:
                    amount = int(before_match.group(1))
                    unit = before_match.group(2)
                    
                    if unit == 'saat':
                        reminder_time = reminder_datetime - datetime.timedelta(hours=amount)
                    else:  # dakika
                        reminder_time = reminder_datetime - datetime.timedelta(minutes=amount)
            else:
                # Varsayılan: 1 saat önce
                reminder_time = reminder_datetime - datetime.timedelta(hours=1)
            
            # Veritabanına kaydet
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            reminder_text = f"🔔 Hatırlatma: {parsed['original_message']}\n⏰ Asıl Etkinlik: {reminder_datetime.strftime('%Y-%m-%d %H:%M')}"
            
            cursor.execute("""
                INSERT INTO reminders (user_id, reminder_text, reminder_time, original_message)
                VALUES (?, ?, ?, ?)
            """, (user_id, reminder_text, reminder_time, message))
            
            reminder_id = cursor.lastrowid
            
            # Görev olarak da kaydet
            cursor.execute("""
                INSERT INTO tasks (user_id, task_text, due_date, priority)
                VALUES (?, ?, ?, ?)
            """, (user_id, message, reminder_datetime, 'high'))
            
            db.commit()
            db.close()
            
            # Scheduler'a ekle
            if reminder_time > datetime.datetime.now():
                self.scheduler.add_job(
                    func=send_callback,
                    trigger=DateTrigger(run_date=reminder_time),
                    args=[user_id, reminder_text],
                    id=f'reminder_{reminder_id}',
                    replace_existing=True
                )
                
                return {
                    'success': True,
                    'reminder_id': reminder_id,
                    'reminder_time': reminder_time,
                    'event_time': reminder_datetime,
                    'message': f"""✅ **Hatırlatma Kaydedildi!**

📝 **Görev:** {message}
⏰ **Etkinlik Zamanı:** {reminder_datetime.strftime('%d.%m.%Y %H:%M')}
🔔 **Hatırlatma:** {reminder_time.strftime('%d.%m.%Y %H:%M')}

Zamanı geldiğinde size hatırlatacağım! 😊"""
                }
            else:
                return {
                    'success': False,
                    'message': '❌ Hatırlatma zamanı geçmişte kalıyor. Lütfen gelecek bir zaman belirtin.'
                }
            
        except Exception as e:
            print(f"❌ Hatırlatma oluşturma hatası: {e}")
            return {
                'success': False,
                'message': f'❌ Hatırlatma kaydedilirken hata oluştu: {str(e)}'
            }
    
    def get_user_tasks(self, user_id):
        """Kullanıcının görevlerini getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT task_text, due_date, priority, is_completed, created_at
                FROM tasks
                WHERE user_id = ? AND is_completed = FALSE
                ORDER BY due_date ASC
                LIMIT 10
            """, (user_id,))
            
            tasks = cursor.fetchall()
            db.close()
            
            if not tasks:
                return "📋 Şu anda aktif göreviniz bulunmuyor."
            
            result = "📋 **Aktif Görevleriniz:**\n\n"
            for i, task in enumerate(tasks, 1):
                task_text, due_date, priority, is_completed, created_at = task
                
                if due_date:
                    due_dt = datetime.datetime.fromisoformat(due_date)
                    due_str = due_dt.strftime('%d.%m.%Y %H:%M')
                    
                    # Öncelik emoji
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                    
                    result += f"{i}. {priority_emoji} {task_text}\n⏰ {due_str}\n\n"
                else:
                    result += f"{i}. ⚪ {task_text}\n\n"
            
            return result
            
        except Exception as e:
            print(f"❌ Görev listeleme hatası: {e}")
            return "❌ Görevler getirilirken hata oluştu."
    
    def get_upcoming_reminders(self, user_id, hours=24):
        """Yaklaşan hatırlatmaları getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            from_time = datetime.datetime.now()
            to_time = from_time + datetime.timedelta(hours=hours)
            
            cursor.execute("""
                SELECT reminder_text, reminder_time, original_message
                FROM reminders
                WHERE user_id = ? AND reminder_time BETWEEN ? AND ? AND is_sent = FALSE
                ORDER BY reminder_time ASC
            """, (user_id, from_time, to_time))
            
            reminders = cursor.fetchall()
            db.close()
            
            if not reminders:
                return f"🕐 Önümüzdeki {hours} saat içinde hatırlatmanız yok."
            
            result = f"🔔 **Önümüzdeki {hours} Saat İçindeki Hatırlatmalar:**\n\n"
            for i, reminder in enumerate(reminders, 1):
                reminder_text, reminder_time, original_message = reminder
                reminder_dt = datetime.datetime.fromisoformat(reminder_time)
                time_str = reminder_dt.strftime('%d.%m.%Y %H:%M')
                
                result += f"{i}. {original_message}\n⏰ {time_str}\n\n"
            
            return result
            
        except Exception as e:
            print(f"❌ Hatırlatma listeleme hatası: {e}")
            return "❌ Hatırlatmalar getirilirken hata oluştu."

# Singleton instance
task_reminder = TaskReminderSystem()

def create_task_reminder(user_id, message, send_callback):
    """Ana hatırlatma oluşturma fonksiyonu"""
    return task_reminder.create_reminder(user_id, message, send_callback)

def get_user_task_list(user_id):
    """Kullanıcı görev listesi"""
    return task_reminder.get_user_tasks(user_id)

def get_user_reminders(user_id, hours=24):
    """Kullanıcı hatırlatmaları"""
    return task_reminder.get_upcoming_reminders(user_id, hours)
