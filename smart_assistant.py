"""
Akıllı öğrenen asistan - Kullanıcı davranışlarını öğrenir ve hatırlar
"""

import sqlite3
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
import dateparser

class SmartAssistant:
    """Öğrenen ve hatırlayan AI asistan"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Veritabanı tablolarını oluştur"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Kullanıcı profilleri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT,
                occupation TEXT,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Öğrenilen bilgiler
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                key_info TEXT,
                value_info TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
            )
        """)
        
        # Konuşma geçmişi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                intent TEXT,
                entities TEXT,
                response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
            )
        """)
        
        # Müsaitlik durumu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date_time TIMESTAMP,
                status TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
            )
        """)
        
        db.commit()
        db.close()
    
    def learn_from_message(self, user_id, message):
        """Mesajdan bilgi öğren"""
        try:
            # Konuşma geçmişine kaydet
            self.store_conversation(user_id, message)
            
            # Kişisel bilgileri çıkar
            personal_info = self.extract_personal_info(message)
            if personal_info:
                self.store_learned_info(user_id, personal_info)
            
            # Müsaitlik bilgilerini çıkar
            availability_info = self.extract_availability(message)
            if availability_info:
                self.store_availability(user_id, availability_info)
            
            return True
        except Exception as e:
            print(f"❌ Öğrenme hatası: {e}")
            return False
    
    def store_conversation(self, user_id, message):
        """Konuşmayı kaydet - Güvenli versiyon"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db = sqlite3.connect(self.db_path, timeout=10.0)
                db.execute("PRAGMA journal_mode=WAL")
                cursor = db.cursor()
                
                intent = self.extract_intent(message)
                entities = self.extract_entities(message)
                
                cursor.execute("""
                    INSERT INTO conversation_history (user_id, message, intent, entities)
                    VALUES (?, ?, ?, ?)
                """, (user_id, message, intent, json.dumps(entities)))
                
                db.commit()
                db.close()
                return True
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    print(f"❌ Veritabanı hatası: {e}")
                    return False
        return False
    
    def store_learned_info(self, user_id, info_dict):
        """Öğrenilen bilgiyi veritabanına kaydet - Güvenli versiyon"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db = sqlite3.connect(self.db_path, timeout=10.0)
                db.execute("PRAGMA journal_mode=WAL")
                cursor = db.cursor()
                
                for category, value in info_dict.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO learned_info
                        (user_id, category, key_info, value_info, confidence)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, category, category, str(value), 0.8))
                
                db.commit()
                db.close()
                return True
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    print(f"❌ Veritabanı hatası: {e}")
                    return False
        return False
    
    def store_availability(self, user_id, availability_info):
        """Müsaitlik bilgisini kaydet - Güvenli versiyon"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db = sqlite3.connect(self.db_path, timeout=10.0)
                db.execute("PRAGMA journal_mode=WAL")
                cursor = db.cursor()
                
                cursor.execute("""
                    INSERT INTO availability (user_id, date_time, status, description)
                    VALUES (?, ?, ?, ?)
                """, (user_id, availability_info['datetime'], availability_info['status'], availability_info['description']))
                
                db.commit()
                db.close()
                return True
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    print(f"❌ Veritabanı hatası: {e}")
                    return False
        return False
    
    def extract_personal_info(self, message):
        """Kişisel bilgileri çıkar"""
        info = {}
        message_lower = message.lower()
        
        # İsim tespiti - daha kapsamlı
        name_patterns = [
            r'adım\s+(\w+)',
            r'ben\s+(\w+)',
            r'ismim\s+(\w+)',
            r'benim adım\s+(\w+)',
            r'adıma\s+(\w+)\s+de',
            r'bana\s+(\w+)\s+de',
            r'name.*?(\w+)',
            r'call me\s+(\w+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info['name'] = match.group(1).capitalize()
                break
        
        # Bot adı öğrenme
        bot_name_patterns = [
            r'senin adın\s+(\w+)',
            r'sana\s+(\w+)\s+diyeyim',
            r'adın\s+(\w+)\s+olsun',
            r'ismin\s+(\w+)',
            r'seni\s+(\w+)\s+çağırayım'
        ]
        
        for pattern in bot_name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info['bot_name'] = match.group(1).capitalize()
                break
        
        # Konum tespiti
        location_patterns = [
            r'(\w+)\'da yaşıyorum',
            r'(\w+)\'de yaşıyorum',
            r'(\w+)\'dayım',
            r'(\w+)\'deyim',
            r'şehrim\s+(\w+)',
            r'(\w+)\'dan geliyorum'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info['location'] = match.group(1).capitalize()
                break
        
        # Meslek tespiti
        job_patterns = [
            r'(\w+)\s+olarak çalışıyorum',
            r'mesleğim\s+(\w+)',
            r'ben\s+(\w+)yım',
            r'(\w+)\s+geliştirici',
            r'işim\s+(\w+)',
            r'(\w+)\s+olarak çalışıyorum'
        ]
        
        for pattern in job_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info['occupation'] = match.group(1)
                break
        
        return info
    
    def extract_availability(self, message):
        """Müsaitlik bilgilerini çıkar"""
        message_lower = message.lower()
        
        # Zaman ifadeleri
        time_patterns = [
            r'yarın\s+(.+)',
            r'bugün\s+(.+)',
            r'gelecek hafta\s+(.+)',
            r'pazartesi\s+(.+)',
        ]
        
        # Aktivite ifadeleri
        busy_keywords = ['toplantı', 'randevu', 'iş', 'çalışma', 'buluşma', 'görüşme']
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                activity = match.group(1)
                
                # Zaman çıkarımı
                try:
                    parsed_time = dateparser.parse(match.group(0), languages=['tr'])
                    if parsed_time:
                        status = 'busy' if any(keyword in activity for keyword in busy_keywords) else 'available'
                        
                        return {
                            'datetime': parsed_time,
                            'status': status,
                            'description': activity
                        }
                except:
                    pass
        
        return None
    
    def extract_intent(self, message):
        """Mesajın amacını tespit et"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['merhaba', 'selam', 'sa', 'slm']):
            return 'greeting'
        elif any(word in message_lower for word in ['adım', 'ismim', 'ben']):
            return 'introduction'
        elif any(word in message_lower for word in ['toplantı', 'randevu', 'iş']):
            return 'scheduling'
        elif any(word in message_lower for word in ['haber', 'analiz', 'trend']):
            return 'news_request'
        elif '?' in message:
            return 'question'
        else:
            return 'general'
    
    def extract_entities(self, message):
        """Varlıkları çıkar (isim, tarih, vb.)"""
        entities = {}
        
        # İsim varlığı
        name_match = re.search(r'adım\s+(\w+)', message.lower())
        if name_match:
            entities['name'] = name_match.group(1)
        
        return entities
    
    def get_user_profile(self, user_id):
        """Kullanıcı profilini getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = db.cursor()
            
            cursor.execute("SELECT * FROM learned_info WHERE user_id = ?", (user_id,))
            learned_info = cursor.fetchall()
            
            cursor.execute("SELECT * FROM availability WHERE user_id = ? ORDER BY date_time DESC", (user_id,))
            availability = cursor.fetchall()
            
            db.close()
            
            return {
                'learned_info': learned_info,
                'availability': availability
            }
        except Exception as e:
            print(f"❌ Profil getirme hatası: {e}")
            return None
    
    def check_availability(self, user_id, check_date=None):
        """Müsaitlik kontrolü"""
        if check_date is None:
            check_date = datetime.now()
        
        try:
            db = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT * FROM availability 
                WHERE user_id = ? AND DATE(date_time) = DATE(?)
                ORDER BY date_time
            """, (user_id, check_date))
            
            results = cursor.fetchall()
            db.close()
            
            return results
        except Exception as e:
            print(f"❌ Müsaitlik kontrol hatası: {e}")
            return []
    
    def generate_response(self, user_id, message):
        """Öğrenilen bilgilere göre yanıt oluştur"""
        message_lower = message.lower()
        
        # Kullanıcı profilini al
        profile = self.get_user_profile(user_id)
        user_name = None
        bot_name = "AI"
        
        if profile and profile['learned_info']:
            for info in profile['learned_info']:
                if info[2] == 'name':  # category column
                    user_name = info[4]  # value_info column
                elif info[2] == 'bot_name':
                    bot_name = info[4]
        
        # Selamlama yanıtları
        greetings = ['merhaba', 'selam', 'sa', 'slm', 'hello', 'hi', 'hey']
        if any(word in message_lower for word in greetings):
            if user_name:
                return f"Merhaba {user_name}! Ben {bot_name}. Nasılsın?"
            else:
                return f"Merhaba! Ben {bot_name}. Adınızı öğrenmek isterim. 'Adım ...' diyebilirsiniz."
        
        # İsim öğrenme tepkileri
        if any(word in message_lower for word in ['adım', 'ismim', 'ben']):
            # İsim çıkar
            name_match = re.search(r'(?:adım|ismim|ben)\s+(\w+)', message_lower)
            if name_match:
                name = name_match.group(1).capitalize()
                return f"Merhaba {name}! Çok güzel bir isim. Sizi artık {name} olarak çağıracağım. Ben {bot_name}'yım."
            else:
                return "İsminizi anlayamadım. 'Adım Mehmet' şeklinde söyleyebilir misiniz?"
        
        # Bot adı öğrenme
        if any(phrase in message_lower for phrase in ['senin adın', 'sana', 'adın', 'ismin']):
            bot_name_match = re.search(r'(?:senin adın|sana|adın|ismin)\s+(\w+)', message_lower)
            if bot_name_match:
                new_bot_name = bot_name_match.group(1).capitalize()
                return f"Tamam! Artık benim adım {new_bot_name} olsun. Teşekkürler!"
            else:
                return f"Benim adım {bot_name}. Bana farklı bir isim vermek ister misiniz?"
        
        # Nasılsın soruları
        if any(word in message_lower for word in ['nasılsın', 'nasıl', 'naber', 'nasilsin']):
            if user_name:
                return f"İyiyim {user_name}, teşekkürler! Sen nasılsın? Size nasıl yardımcı olabilirim?"
            else:
                return "İyiyim, teşekkürler! Sen nasılsın? Size nasıl yardımcı olabilirim?"
        
        # Müsaitlik sorgusu
        if any(word in message_lower for word in ['müsait', 'boş', 'randevu']):
            availability = self.check_availability(user_id)
            if availability:
                return f"Bugün için {len(availability)} randevunuz var."
            else:
                if user_name:
                    return f"{user_name}, bugün müsait görünüyorsunuz!"
                else:
                    return "Bugün müsait görünüyorsunuz!"
        
        # Teşekkür yanıtları
        if any(word in message_lower for word in ['teşekkür', 'sağol', 'thanks', 'tesekkur']):
            if user_name:
                return f"Rica ederim {user_name}! Size yardımcı olmaktan mutluluk duyarım."
            else:
                return "Rica ederim! Size yardımcı olmaktan mutluluk duyarım."
        
        # Hoşça kal yanıtları  
        if any(word in message_lower for word in ['hoşça kal', 'görüşürüz', 'bay', 'bye']):
            if user_name:
                return f"Hoşça kal {user_name}! Görüşmek üzere!"
            else:
                return "Hoşça kalın! Görüşmek üzere!"
        
        # Genel yardım
        if any(word in message_lower for word in ['yardım', 'help', 'ne yapabilirsin']):
            help_text = f"Merhaba"
            if user_name:
                help_text += f" {user_name}"
            help_text += f"! Ben {bot_name}. Size şunlarda yardımcı olabilirim:\n\n"
            help_text += "🧠 Akıllı özellikler:\n"
            help_text += "• Adınızı öğrenir ve hatırlarım\n"
            help_text += "• Randevularınızı takip ederim\n"
            help_text += "• Sohbet geçmişinizi hatırlarım\n\n"
            help_text += "📰 Haber özellikleri:\n"
            help_text += "• /haber - Son haberleri getiririm\n"
            help_text += "• /analiz - Haber analizi yaparım\n\n"
            help_text += "Benimle normal bir insan gibi konuşabilirsiniz!"
            return help_text
        
# Global instance
smart_assistant = SmartAssistant()

async def handle_smart_message(update, context, message):
    """Akıllı mesaj işleme"""
    user_id = update.effective_user.id
    
    try:
        # Mesajdan öğren
        smart_assistant.learn_from_message(user_id, message)
        
        # Yanıt oluştur
        response = smart_assistant.generate_response(user_id, message)
        
        if response:
            return response
        return False
    except Exception as e:
        print(f"❌ Akıllı mesaj işleme hatası: {e}")
        return False

async def handle_learn_info(update, context):
    """Bilgi öğrenme komutu"""
    message = update.message.text
    user_id = update.effective_user.id
    
    try:
        success = smart_assistant.learn_from_message(user_id, message)
        if success:
            return "✅ Bilginizi öğrendim ve hatırlayacağım!"
        else:
            return "⚠️ Bilgi öğrenirken bir sorun oldu."
    except Exception as e:
        print(f"❌ Bilgi öğrenme hatası: {e}")
        return "❌ Öğrenme sırasında hata oluştu."

async def handle_availability_check(update, context):
    """Müsaitlik kontrol komutu"""
    user_id = update.effective_user.id
    
    try:
        availability = smart_assistant.check_availability(user_id)
        
        if availability:
            response = "📅 Bugünkü programınız:\n"
            for item in availability:
                date_time = item[2]  # date_time column
                status = item[3]     # status column
                description = item[4] # description column
                response += f"• {date_time}: {description} ({status})\n"
        else:
            response = "📅 Bugün için herhangi bir randevunuz yok. Müsaitsiniz!"
        
        await update.message.reply_text(response)
        return response
    except Exception as e:
        print(f"❌ Müsaitlik kontrol hatası: {e}")
        return "❌ Müsaitlik kontrol edilemedi."

async def show_user_profile(update, context):
    """Kullanıcı profilini göster"""
    user_id = update.effective_user.id
    
    try:
        profile = smart_assistant.get_user_profile(user_id)
        
        if not profile or not profile['learned_info']:
            await update.message.reply_text("👤 Henüz hakkınızda bilgi öğrenmedim. Biraz konuşalım!")
            return
        
        response = "👤 **Profiliniz:**\n\n"
        
        # Öğrenilen bilgileri grupla
        info_groups = {}
        for info in profile['learned_info']:
            category = info[2]  # category column
            value = info[4]     # value_info column
            if category not in info_groups:
                info_groups[category] = []
            info_groups[category].append(value)
        
        for category, values in info_groups.items():
            response += f"**{category.capitalize()}:** {', '.join(values)}\n"
        
        # Müsaitlik bilgileri
        if profile['availability']:
            response += f"\n📅 **Yaklaşan Randevular:** {len(profile['availability'])} adet\n"
        
        await update.message.reply_text(response)
        return response
    except Exception as e:
        print(f"❌ Profil gösterme hatası: {e}")
        return "❌ Profil gösterilemedi."
        self.db_path = db_path
        self.setup_learning_database()
    
    def setup_learning_database(self):
        """Öğrenme veritabanını kur"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Kullanıcı profili tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                preferences TEXT,
                habits TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Öğrenilen bilgiler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_info (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                category TEXT,
                key_info TEXT,
                value_info TEXT,
                confidence REAL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Randevu ve müsaitlik tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS availability (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                date_start TEXT,
                date_end TEXT,
                event_type TEXT,
                description TEXT,
                is_busy BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Konuşma geçmişi ve bağlam
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                message TEXT,
                intent TEXT,
                entities TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.commit()
        db.close()
    
    def learn_from_message(self, user_id, message):
        """Mesajdan öğren"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Konuşma geçmişine ekle
        intent = self.extract_intent(message)
        entities = self.extract_entities(message)
        
        cursor.execute("""
            INSERT INTO conversation_history (user_id, message, intent, entities)
            VALUES (?, ?, ?, ?)
        """, (user_id, message, intent, json.dumps(entities)))
        
        # Randevu/müsaitlik bilgisi varsa öğren
        if self.is_availability_info(message):
            self.learn_availability(user_id, message)
        
        # Kişisel bilgi varsa öğren
        personal_info = self.extract_personal_info(message)
        if personal_info:
            self.store_learned_info(user_id, personal_info)
        
        db.commit()
        db.close()
    
    def extract_intent(self, message):
        """Mesajın amacını çıkar"""
        message_lower = message.lower()
        
        intents = {
            "randevu": ["randevu", "buluşma", "toplantı", "meeting"],
            "müsaitlik": ["müsait", "boş", "uygun", "available"],
            "hatırlatma": ["hatırlat", "reminder", "unutma"],
            "not": ["not al", "kaydet", "remember"],
            "soru": ["ne zaman", "nasıl", "nerede", "kim", "?"],
            "araştırma": ["araştır", "bul", "search", "ara"]
        }
        
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "genel"
    
    def extract_entities(self, message):
        """Varlıkları çıkar (tarih, kişi, yer vs)"""
        entities = {}
        
        # Tarih çıkarma
        dates = self.extract_dates(message)
        if dates:
            entities["dates"] = dates
        
        # Kişi isimleri (büyük harfle başlayan kelimeler)
        names = re.findall(r'\b[A-ZÇĞıİÖŞÜ][a-zçğıiöşü]+\b', message)
        if names:
            entities["people"] = names
        
        # Yerler
        places = re.findall(r'\b(?:ofis|ev|şirket|hastane|okul|üniversite)\b', message.lower())
        if places:
            entities["places"] = places
        
        return entities
    
    def extract_dates(self, message):
        """Metinden tarihleri çıkar"""
        try:
            # Türkçe tarih ifadeleri
            date_patterns = [
                r'yarın', r'bugün', r'dün',
                r'gelecek hafta', r'bu hafta', r'geçen hafta',
                r'gelecek ay', r'bu ay',
                r'\d{1,2}[./]\d{1,2}[./]\d{2,4}',
                r'\d{1,2}\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)',
                r'(pazartesi|salı|çarşamba|perşembe|cuma|cumartesi|pazar)'
            ]
            
            found_dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, message.lower())
                found_dates.extend(matches)
            
            # dateparser ile gerçek tarihlere çevir
            parsed_dates = []
            for date_str in found_dates:
                parsed = dateparser.parse(date_str, languages=['tr'])
                if parsed:
                    parsed_dates.append(parsed.isoformat())
            
            return parsed_dates
        except:
            return []
    
    def is_availability_info(self, message):
        """Müsaitlik bilgisi içeriyor mu?"""
        keywords = ["randevu", "müsait", "boş", "meşgul", "toplantı", "buluşma", "uygun"]
        return any(keyword in message.lower() for keyword in keywords)
    
    def learn_availability(self, user_id, message):
        """Müsaitlik bilgisini öğren"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        dates = self.extract_dates(message)
        is_busy = any(word in message.lower() for word in ["randevu", "toplantı", "meşgul", "dolu"])
        
        for date_str in dates:
            cursor.execute("""
                INSERT INTO availability (user_id, date_start, event_type, description, is_busy)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, date_str, "learned", message[:100], is_busy))
        
        db.commit()
        db.close()
    
    def extract_personal_info(self, message):
        """Kişisel bilgileri çıkar"""
        info = {}
        message_lower = message.lower()
        
        # İsim öğrenme
        if "adım" in message_lower or "ismim" in message_lower:
            # "Adım Mehmet" -> Mehmet
            name_match = re.search(r'(?:adım|ismim)\s+(\w+)', message_lower)
            if name_match:
                info["name"] = name_match.group(1).title()
        
        # Meslek öğrenme
        if "çalışıyorum" in message_lower or "işim" in message_lower:
            job_match = re.search(r'(\w+(?:\s+\w+)?)\s+(?:olarak\s+)?çalışıyorum', message_lower)
            if job_match:
                info["job"] = job_match.group(1)
        
        # Sevdiği şeyler
        if "seviyorum" in message_lower or "beğeniyorum" in message_lower:
            like_match = re.search(r'(\w+(?:\s+\w+)?)\s+seviyorum', message_lower)
            if like_match:
                info["likes"] = info.get("likes", []) + [like_match.group(1)]
        
        return info
    
    def store_learned_info(self, user_id, info):
        """Öğrenilen bilgiyi sakla"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        for category, value in info.items():
            cursor.execute("""
                INSERT OR REPLACE INTO learned_info 
                (user_id, category, key_info, value_info, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, category, category, str(value), 0.8))
        
        db.commit()
        db.close()
    
    def check_availability(self, user_id, target_date):
        """Belirli tarihte müsait mi kontrol et"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT * FROM availability 
            WHERE user_id = ? AND date_start = ? AND is_busy = TRUE
        """, (user_id, target_date.isoformat()))
        
        busy_events = cursor.fetchall()
        db.close()
        
        return len(busy_events) == 0  # Boş ise müsait
    
    def get_user_context(self, user_id):
        """Kullanıcı bağlamını al"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Son konuşmalar
        cursor.execute("""
            SELECT message, intent, timestamp FROM conversation_history 
            WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5
        """, (user_id,))
        recent_conversations = cursor.fetchall()
        
        # Öğrenilen bilgiler
        cursor.execute("""
            SELECT category, value_info, confidence FROM learned_info 
            WHERE user_id = ?
        """, (user_id,))
        learned_info = cursor.fetchall()
        
        # Yaklaşan randevular
        cursor.execute("""
            SELECT date_start, description FROM availability 
            WHERE user_id = ? AND date_start > ? AND is_busy = TRUE
            ORDER BY date_start LIMIT 3
        """, (user_id, datetime.now().isoformat()))
        upcoming_events = cursor.fetchall()
        
        db.close()
        
        return {
            "recent_conversations": recent_conversations,
            "learned_info": dict([(info[0], info[1]) for info in learned_info]),
            "upcoming_events": upcoming_events
        }
    
    def generate_smart_response(self, user_id, message):
        """Akıllı yanıt oluştur"""
        context = self.get_user_context(user_id)
        intent = self.extract_intent(message)
        
        # Kişiselleştirilmiş yanıt
        if "name" in context["learned_info"]:
            greeting = f"Merhaba {context['learned_info']['name']}! "
        else:
            greeting = "Merhaba! "
        
        if intent == "müsaitlik":
            dates = self.extract_dates(message)
            if dates:
                # Müsaitlik kontrolü
                responses = []
                for date_str in dates:
                    date_obj = dateparser.parse(date_str)
                    if date_obj:
                        is_available = self.check_availability(user_id, date_obj)
                        status = "müsaitsiniz" if is_available else "randevunuz var"
                        responses.append(f"{date_obj.strftime('%d.%m.%Y')} tarihinde {status}")
                
                return greeting + "\n".join(responses)
        
        elif intent == "randevu" and context["upcoming_events"]:
            response = greeting + "Yaklaşan randevularınız:\n"
            for event in context["upcoming_events"]:
                date = dateparser.parse(event[0])
                if date:
                    response += f"• {date.strftime('%d.%m.%Y %H:%M')} - {event[1]}\n"
            return response
        
        return greeting + "Size nasıl yardımcı olabilirim?"
    
    def smart_research(self, user_id, query):
        """Akıllı araştırma - kullanıcı profiline göre"""
        context = self.get_user_context(user_id)
        
        # Kullanıcının ilgi alanlarına göre araştırmayı özelleştir
        if "job" in context["learned_info"]:
            job = context["learned_info"]["job"]
            enhanced_query = f"{query} {job} related"
        else:
            enhanced_query = query
        
        # Araştırma sonuçlarını kişiselleştir
        return f"'{enhanced_query}' konusunda araştırma yapıyorum..."

# Global smart assistant instance (ikinci tanım silindi)

async def handle_availability_check(update, context):
    """Müsaitlik kontrolü komutu"""
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    dates = smart_assistant.extract_dates(text)
    if not dates:
        return "📅 Lütfen bir tarih belirtin. Örnek: 'yarın müsait miyim?'"
    
    response = "📅 **Müsaitlik Durumu**\n\n"
    for date_str in dates:
        date_obj = dateparser.parse(date_str)
        if date_obj:
            is_available = smart_assistant.check_availability(user_id, date_obj)
            status = "✅ Müsaitsiniz" if is_available else "❌ Randevunuz var"
            response += f"• {date_obj.strftime('%d.%m.%Y')}: {status}\n"
    
    return response

async def handle_learn_info(update, context):
    """Bilgi öğrenme komutu"""
    user_id = str(update.effective_user.id)
    message = update.message.text
    
    # Bilgiyi öğren
    smart_assistant.learn_from_message(user_id, message)
    
    return "🧠 Anladım ve kaydettim! Bu bilgiyi bundan sonra hatırlayacağım."

async def show_user_profile(update, context):
    """Kullanıcı profilini göster"""
    user_id = str(update.effective_user.id)
    context_data = smart_assistant.get_user_context(user_id)
    
    response = "👤 **Profiliniz**\n\n"
    
    # Öğrenilen bilgiler
    if context_data["learned_info"]:
        response += "🧠 **Hakkınızda Bildiklerim:**\n"
        for category, value in context_data["learned_info"].items():
            if category == "name":
                response += f"• İsim: {value}\n"
            elif category == "job":
                response += f"• Meslek: {value}\n"
            elif category == "likes":
                response += f"• Sevdikleri: {value}\n"
            else:
                response += f"• {category}: {value}\n"
        response += "\n"
    
    # Yaklaşan etkinlikler
    if context_data["upcoming_events"]:
        response += "📅 **Yaklaşan Randevular:**\n"
        for event in context_data["upcoming_events"]:
            date = dateparser.parse(event[0])
            if date:
                response += f"• {date.strftime('%d.%m.%Y %H:%M')} - {event[1][:50]}...\n"
        response += "\n"
    
    # Son konuşmalar
    if context_data["recent_conversations"]:
        response += "💬 **Son Konuşmalar:**\n"
        for conv in context_data["recent_conversations"][:3]:
            timestamp = conv[2]
            response += f"• {conv[1]} ({timestamp})\n"
    
    if len(response) < 50:
        response += "Henüz sizin hakkınızda bilgi öğrenmedim. Benimle konuşarak beni eğitebilirsiniz!"
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return response
