"""
Kişisel Not ve Akıllı Ajanda Yönetimi
Kullanıcı bazlı notlar ve etkinlik planlama sistemi
"""

import sqlite3
import datetime
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PersonalNote:
    """Kişisel not yapısı"""
    id: int
    user_id: int
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    priority: str = "normal"  # low, normal, high, urgent

@dataclass
class ScheduleEvent:
    """Ajanda etkinliği yapısı"""
    id: int
    user_id: int
    title: str
    description: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    event_type: str  # meeting, conference, personal, work, etc.
    location: str
    reminder_minutes: int = 30
    status: str = "planned"  # planned, confirmed, cancelled, completed

class PersonalNotesManager:
    """Kullanıcı bazlı kişisel not yönetimi"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Veritabanı tablolarını oluştur"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Kişisel notlar tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personal_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    tags TEXT,  -- JSON array as text
                    priority TEXT DEFAULT 'normal',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_archived INTEGER DEFAULT 0
                )
            """)
            
            # Ajanda etkinlikleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedule_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_datetime TEXT NOT NULL,  -- ISO format
                    end_datetime TEXT NOT NULL,    -- ISO format
                    event_type TEXT DEFAULT 'general',
                    location TEXT,
                    reminder_minutes INTEGER DEFAULT 30,
                    status TEXT DEFAULT 'planned',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Hızlı arama için indeksler
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_user_category ON personal_notes (user_id, category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_user_priority ON personal_notes (user_id, priority)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_datetime ON schedule_events (user_id, start_datetime)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_type ON schedule_events (user_id, event_type)")
            
            db.commit()
            db.close()
            print("✅ Kişisel not ve ajanda tabloları oluşturuldu!")
            
        except Exception as e:
            print(f"❌ Veritabanı kurulum hatası: {e}")
    
    def add_note(self, user_id: int, title: str, content: str, 
                 category: str = "general", tags: List[str] = None, 
                 priority: str = "normal") -> bool:
        """Yeni not ekle"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            tags_str = ",".join(tags) if tags else ""
            
            cursor.execute("""
                INSERT INTO personal_notes (user_id, title, content, category, tags, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, title, content, category, tags_str, priority))
            
            db.commit()
            db.close()
            print(f"✅ Not kaydedildi: {title}")
            return True
            
        except Exception as e:
            print(f"❌ Not kaydetme hatası: {e}")
            return False
    
    def search_notes(self, user_id: int, query: str = "", 
                    category: str = "", priority: str = "") -> List[Dict]:
        """Notlarda arama yap"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            sql = """
                SELECT id, title, content, category, tags, priority, created_at, updated_at
                FROM personal_notes 
                WHERE user_id = ? AND is_archived = 0
            """
            params = [user_id]
            
            if query:
                sql += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
                query_param = f"%{query}%"
                params.extend([query_param, query_param, query_param])
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            if priority:
                sql += " AND priority = ?"
                params.append(priority)
            
            sql += " ORDER BY updated_at DESC"
            
            cursor.execute(sql, params)
            notes = cursor.fetchall()
            db.close()
            
            return [{
                'id': note[0], 'title': note[1], 'content': note[2],
                'category': note[3], 'tags': note[4].split(',') if note[4] else [],
                'priority': note[5], 'created_at': note[6], 'updated_at': note[7]
            } for note in notes]
            
        except Exception as e:
            print(f"❌ Not arama hatası: {e}")
            return []
    
    def get_user_categories(self, user_id: int) -> List[str]:
        """Kullanıcının not kategorilerini getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT DISTINCT category FROM personal_notes 
                WHERE user_id = ? AND is_archived = 0
                ORDER BY category
            """, (user_id,))
            
            categories = [row[0] for row in cursor.fetchall()]
            db.close()
            return categories
            
        except Exception as e:
            print(f"❌ Kategori getirme hatası: {e}")
            return []
    
    def get_user_notes(self, user_id: int, limit: int = 20) -> List[tuple]:
        """Kullanıcının notlarını getir - tuple formatında"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT id, user_id, title, content, category, created_at, updated_at, priority
                FROM personal_notes 
                WHERE user_id = ? AND is_archived = 0
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            notes = cursor.fetchall()
            db.close()
            return notes
            
        except Exception as e:
            print(f"❌ Not getirme hatası: {e}")
            return []
    
    def get_user_notes_by_date(self, user_id: int, date: datetime.datetime) -> List[tuple]:
        """📅 Belirli tarihteki notları getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Tarihi string formatına çevir
            date_str = date.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT id, user_id, title, content, category, created_at, updated_at, priority
                FROM personal_notes 
                WHERE user_id = ? AND date(scheduled_date) = ? AND is_archived = 0
                ORDER BY created_at DESC
            """, (user_id, date_str))
            
            notes = cursor.fetchall()
            db.close()
            
            return notes
            
        except Exception as e:
            print(f"❌ Tarihli not getirme hatası: {e}")
            return []

class SmartAgendaManager:
    """Akıllı ajanda ve etkinlik yönetimi"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
    
    def add_event(self, user_id: int, title: str, start_datetime: datetime.datetime,
                  end_datetime: datetime.datetime, description: str = "",
                  event_type: str = "general", location: str = "",
                  reminder_minutes: int = 30) -> bool:
        """Yeni etkinlik ekle"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO schedule_events 
                (user_id, title, description, start_datetime, end_datetime, 
                 event_type, location, reminder_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, title, description, 
                  start_datetime.isoformat(), end_datetime.isoformat(),
                  event_type, location, reminder_minutes))
            
            db.commit()
            db.close()
            print(f"✅ Etkinlik kaydedildi: {title}")
            return True
            
        except Exception as e:
            print(f"❌ Etkinlik kaydetme hatası: {e}")
            return False
    
    def check_availability(self, user_id: int, start_datetime: datetime.datetime,
                          end_datetime: datetime.datetime) -> Tuple[bool, List[Dict]]:
        """Belirtilen zaman aralığında müsaitlik kontrol et"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT id, title, start_datetime, end_datetime, event_type, location
                FROM schedule_events 
                WHERE user_id = ? AND status != 'cancelled'
                AND (
                    (start_datetime <= ? AND end_datetime > ?) OR
                    (start_datetime < ? AND end_datetime >= ?) OR
                    (start_datetime >= ? AND start_datetime < ?)
                )
                ORDER BY start_datetime
            """, (user_id, 
                  start_datetime.isoformat(), start_datetime.isoformat(),
                  end_datetime.isoformat(), end_datetime.isoformat(),
                  start_datetime.isoformat(), end_datetime.isoformat()))
            
            conflicts = cursor.fetchall()
            db.close()
            
            is_available = len(conflicts) == 0
            
            conflict_events = [{
                'id': c[0], 'title': c[1], 'start': c[2], 'end': c[3],
                'type': c[4], 'location': c[5]
            } for c in conflicts]
            
            return is_available, conflict_events
            
        except Exception as e:
            print(f"❌ Müsaitlik kontrol hatası: {e}")
            return False, []
    
    def get_events_for_date(self, user_id: int, date: datetime.date) -> List[Dict]:
        """Belirli bir tarihteki etkinlikleri getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            start_of_day = datetime.datetime.combine(date, datetime.time.min)
            end_of_day = datetime.datetime.combine(date, datetime.time.max)
            
            cursor.execute("""
                SELECT id, title, description, start_datetime, end_datetime, 
                       event_type, location, status
                FROM schedule_events 
                WHERE user_id = ? AND status != 'cancelled'
                AND start_datetime >= ? AND start_datetime <= ?
                ORDER BY start_datetime
            """, (user_id, start_of_day.isoformat(), end_of_day.isoformat()))
            
            events = cursor.fetchall()
            db.close()
            
            return [{
                'id': e[0], 'title': e[1], 'description': e[2],
                'start': e[3], 'end': e[4], 'type': e[5],
                'location': e[6], 'status': e[7]
            } for e in events]
            
        except Exception as e:
            print(f"❌ Günlük etkinlik getirme hatası: {e}")
            return []
    
    def get_user_events(self, user_id: int, limit: int = 20) -> List[tuple]:
        """Kullanıcının etkinliklerini getir - tuple formatında"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT id, user_id, title, start_datetime, end_datetime, event_type, location, description
                FROM schedule_events 
                WHERE user_id = ? AND status != 'cancelled'
                ORDER BY start_datetime ASC
                LIMIT ?
            """, (user_id, limit))
            
            events = cursor.fetchall()
            db.close()
            return events
            
        except Exception as e:
            print(f"❌ Etkinlik getirme hatası: {e}")
            return []
    
    def get_user_events_by_date(self, user_id: int, date: datetime.datetime) -> List[tuple]:
        """📅 Belirli tarihteki etkinlikleri getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Tarihi string formatına çevir
            date_str = date.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT id, user_id, title, start_datetime, end_datetime, event_type, location, description
                FROM schedule_events 
                WHERE user_id = ? AND date(start_datetime) = ? AND status != 'cancelled'
                ORDER BY start_datetime ASC
            """, (user_id, date_str))
            
            events = cursor.fetchall()
            db.close()
            
            return events
            
        except Exception as e:
            print(f"❌ Tarihli etkinlik getirme hatası: {e}")
            return []
    
    def suggest_alternative_times(self, user_id: int, 
                                 preferred_datetime: datetime.datetime,
                                 duration_minutes: int,
                                 search_days: int = 7) -> List[Dict]:
        """Alternatif zaman önerileri"""
        try:
            suggestions = []
            current_date = preferred_datetime.date()
            
            for day_offset in range(search_days):
                check_date = current_date + datetime.timedelta(days=day_offset)
                
                # Çalışma saatleri içinde kontrol et (9:00-18:00)
                for hour in range(9, 18):
                    for minute in [0, 30]:  # 30'ar dakika arayla
                        start_time = datetime.datetime.combine(check_date, 
                                                             datetime.time(hour, minute))
                        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
                        
                        # 18:00'ı aşmasın
                        if end_time.hour >= 18:
                            continue
                        
                        is_available, _ = self.check_availability(user_id, start_time, end_time)
                        
                        if is_available:
                            suggestions.append({
                                'start_datetime': start_time,
                                'end_datetime': end_time,
                                'date_str': start_time.strftime('%d %B %Y, %A'),
                                'time_str': f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
                            })
                        
                        # En fazla 5 öneri
                        if len(suggestions) >= 5:
                            return suggestions
            
            return suggestions
            
        except Exception as e:
            print(f"❌ Alternatif zaman önerisi hatası: {e}")
            return []

class PersonalAssistantCore:
    """Kişisel asistan ana sınıfı - Not ve ajanda entegrasyonu"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.notes_manager = PersonalNotesManager(db_path)
        self.agenda_manager = SmartAgendaManager(db_path)
    
    def parse_note_from_message(self, user_id: int, message: str) -> bool:
        """Mesajdan not çıkarıp kaydet"""
        try:
            message_lower = message.lower()
            
            # Not alma kalıpları
            note_patterns = [
                r'not al[:\s]*(.*)',
                r'kaydet[:\s]*(.*)',
                r'unutma[:\s]*(.*)',
                r'yazdır[:\s]*(.*)',
                r'önemli[:\s]*(.*)'
            ]
            
            for pattern in note_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    content = match.group(1).strip()
                    if len(content) > 5:  # Çok kısa notları alma
                        
                        # Kategori belirle
                        category = self.detect_note_category(content)
                        priority = self.detect_priority(content)
                        
                        title = content[:50] + "..." if len(content) > 50 else content
                        
                        return self.notes_manager.add_note(
                            user_id, title, content, category, [], priority
                        )
            
            return False
            
        except Exception as e:
            print(f"❌ Not çıkarma hatası: {e}")
            return False
    
    def parse_event_from_message(self, user_id: int, message: str) -> bool:
        """Mesajdan etkinlik çıkarıp kaydet"""
        try:
            # Tarih ve saat çıkarma
            datetime_info = self.extract_datetime_from_message(message)
            if not datetime_info:
                return False
            
            start_datetime = datetime_info['start']
            duration = datetime_info.get('duration', 60)  # Default 1 saat
            end_datetime = start_datetime + datetime.timedelta(minutes=duration)
            
            # Etkinlik başlığı ve tipi
            title = self.extract_event_title(message)
            event_type = self.detect_event_type(message)
            location = self.extract_location(message)
            
            return self.agenda_manager.add_event(
                user_id, title, start_datetime, end_datetime,
                message, event_type, location
            )
            
        except Exception as e:
            print(f"❌ Etkinlik çıkarma hatası: {e}")
            return False
    
    def check_availability_from_message(self, user_id: int, message: str) -> str:
        """Mesajdan müsaitlik kontrolü yap"""
        try:
            datetime_info = self.extract_datetime_from_message(message)
            if not datetime_info:
                return "❌ Tarih/saat bilgisi anlaşılamadı."
            
            start_datetime = datetime_info['start']
            duration = datetime_info.get('duration', 60)
            end_datetime = start_datetime + datetime.timedelta(minutes=duration)
            
            is_available, conflicts = self.agenda_manager.check_availability(
                user_id, start_datetime, end_datetime
            )
            
            if is_available:
                return f"✅ {start_datetime.strftime('%d %B %Y, %H:%M')} tarihinde müsaitsiniz!"
            else:
                response = f"❌ {start_datetime.strftime('%d %B %Y, %H:%M')} tarihinde çakışma var:\n\n"
                
                for conflict in conflicts:
                    start_time = datetime.datetime.fromisoformat(conflict['start'])
                    end_time = datetime.datetime.fromisoformat(conflict['end'])
                    response += f"🔸 **{conflict['title']}**\n"
                    response += f"   📅 {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}\n"
                    if conflict['location']:
                        response += f"   📍 {conflict['location']}\n"
                    response += "\n"
                
                # Alternatif öneriler
                alternatives = self.agenda_manager.suggest_alternative_times(
                    user_id, start_datetime, duration
                )
                
                if alternatives:
                    response += "💡 **Alternatif zamanlar:**\n"
                    for alt in alternatives[:3]:
                        response += f"🔸 {alt['date_str']} - {alt['time_str']}\n"
                
                return response
            
        except Exception as e:
            print(f"❌ Müsaitlik kontrol hatası: {e}")
            return "❌ Müsaitlik kontrolünde hata oluştu."
    
    def detect_note_category(self, content: str) -> str:
        """Not kategorisini algıla"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['toplantı', 'konferans', 'iş', 'proje', 'görev']):
            return 'work'
        elif any(word in content_lower for word in ['doktor', 'hastane', 'sağlık', 'ilaç']):
            return 'health'
        elif any(word in content_lower for word in ['market', 'alışveriş', 'al', 'satın']):
            return 'shopping'
        elif any(word in content_lower for word in ['öğren', 'ders', 'eğitim', 'kitap']):
            return 'learning'
        else:
            return 'personal'
    
    def detect_priority(self, content: str) -> str:
        """Öncelik seviyesini algıla"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['acil', 'urgent', 'hemen', 'çok önemli']):
            return 'urgent'
        elif any(word in content_lower for word in ['önemli', 'important', 'kritik']):
            return 'high'
        elif any(word in content_lower for word in ['sonra', 'later', 'ertelenebilir']):
            return 'low'
        else:
            return 'normal'
    
    def extract_datetime_from_message(self, message: str) -> Optional[Dict]:
        """GELİŞMİŞ mesajdan tarih/saat bilgisi çıkar"""
        try:
            message_lower = message.lower()
            now = datetime.datetime.now()
            
            # 1. "05.09.2025" gibi tam tarih formatı
            full_date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', message_lower)
            if full_date_match:
                day = int(full_date_match.group(1))
                month = int(full_date_match.group(2))
                year = int(full_date_match.group(3))
                
                # Saat kontrolü
                time_match = re.search(r'saat\s*(\d{1,2}):?(\d{0,2})', message_lower)
                hour = int(time_match.group(1)) if time_match else 10
                minute = int(time_match.group(2)) if time_match and time_match.group(2) else 0
                
                target_date = datetime.datetime(year, month, day, hour, minute)
                
                return {
                    'start': target_date,
                    'duration': self.extract_duration(message)
                }
            
            # 2. "ayın 10'unda" kalıbı
            month_day_match = re.search(r'ayın\s*(\d{1,2})', message_lower)
            if month_day_match:
                day = int(month_day_match.group(1))
                
                # Saat kontrolü
                time_match = re.search(r'saat\s*(\d{1,2}):?(\d{0,2})', message_lower)
                hour = int(time_match.group(1)) if time_match else 10
                minute = int(time_match.group(2)) if time_match and time_match.group(2) else 0
                
                target_date = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                
                return {
                    'start': target_date,
                    'duration': self.extract_duration(message)
                }
            
            # 3. "yarın", "bugün" gibi rölatif tarihler
            if 'yarın' in message_lower:
                tomorrow = now + datetime.timedelta(days=1)
                
                # Saat kontrolü
                time_match = re.search(r'saat\s*(\d{1,2}):?(\d{0,2})', message_lower)
                hour = int(time_match.group(1)) if time_match else 10
                minute = int(time_match.group(2)) if time_match and time_match.group(2) else 0
                
                target_date = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                return {
                    'start': target_date,
                    'duration': self.extract_duration(message)
                }
            
            # 4. "bugün" 
            if 'bugün' in message_lower:
                # Saat kontrolü
                time_match = re.search(r'saat\s*(\d{1,2}):?(\d{0,2})', message_lower)
                hour = int(time_match.group(1)) if time_match else 10
                minute = int(time_match.group(2)) if time_match and time_match.group(2) else 0
                
                target_date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                return {
                    'start': target_date,
                    'duration': self.extract_duration(message)
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Tarih çıkarma hatası: {e}")
            return None
    
    def extract_duration(self, message: str) -> int:
        """Süre bilgisi çıkar (dakika olarak)"""
        # Basit süre çıkarma
        if 'konferans' in message.lower():
            return 120  # 2 saat
        elif 'toplantı' in message.lower():
            return 60   # 1 saat
        elif 'görüşme' in message.lower():
            return 90   # 1.5 saat
        else:
            return 60   # Default 1 saat
    
    def extract_event_title(self, message: str) -> str:
        """Etkinlik başlığını çıkar"""
        # Mesajın ilk 50 karakterini başlık olarak al
        return message[:50].strip()
    
    def detect_event_type(self, message: str) -> str:
        """Etkinlik tipini algıla"""
        message_lower = message.lower()
        
        if 'konferans' in message_lower:
            return 'conference'
        elif 'toplantı' in message_lower:
            return 'meeting'
        elif 'görüşme' in message_lower:
            return 'appointment'
        elif 'ders' in message_lower:
            return 'education'
        else:
            return 'general'
    
    def extract_location(self, message: str) -> str:
        """Konum bilgisi çıkar"""
        # Basit konum çıkarma
        location_keywords = ['de', 'da', 'te', 'ta']
        # Bu kısım daha gelişmiş NLP ile yapılabilir
        return ""
