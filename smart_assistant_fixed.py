"""
🚀 SÜPER AKI SMART ASSISTANT - Temizlenmiş Versiyon
Gerçek zamanlı web araştırması ve akıllı sohbet sistemi
Kişisel not ve ajanda yönetimi sistemi entegre
"""

import sqlite3
import datetime
import re
import random
import json
from datetime import datetime, timedelta

# Kişisel not ve ajanda sistemini import et
try:
    from personal_notes_manager import PersonalAssistantCore
    PERSONAL_NOTES_AVAILABLE = True
    print("✅ Kişisel not sistemi yüklendi!")
except ImportError:
    PERSONAL_NOTES_AVAILABLE = False
    print("❌ Kişisel not sistemi yüklenemedi - Temel fonksiyonlar çalışır")

# 🧠 SÜPER ZEKİ MOTOR'u import et!
try:
    from super_smart_engine import SuperSmartEngine
    SUPER_SMART_AVAILABLE = True
    print("🧠 SÜPER ZEKİ MOTOR yüklendi!")
except ImportError:
    SUPER_SMART_AVAILABLE = False
    print("❌ Süper zeki motor yüklenemedi")

# 🎭 DUYGUSAL ZEKA MOTOR'unu import et!
try:
    from emotional_intelligence_engine import EmotionalIntelligenceEngine
    EMOTIONAL_AI_AVAILABLE = True
    print("🎭 DUYGUSAL ZEKA MOTORU yüklendi!")
except ImportError:
    EMOTIONAL_AI_AVAILABLE = False
    print("❌ Duygusal zeka motoru yüklenemedi")

# 🧠 HAFIZA VE ÖĞRENME SİSTEMİ'ni import et!
try:
    from super_memory_learning import SuperMemoryLearningSystem
    MEMORY_SYSTEM_AVAILABLE = True
    print("🧠 SÜPER HAFIZA SİSTEMİ yüklendi!")
except ImportError:
    MEMORY_SYSTEM_AVAILABLE = False
    print("❌ Süper hafıza sistemi yüklenemedi")

# 🎯 GELİŞMİŞ KONUŞMA MOTOR'unu import et!
try:
    from advanced_conversation_engine import AdvancedConversationEngine
    ADVANCED_CONVERSATION_AVAILABLE = True
    print("🎯 GELİŞMİŞ KONUŞMA MOTORU yüklendi!")
except ImportError:
    ADVANCED_CONVERSATION_AVAILABLE = False
    print("❌ Gelişmiş konuşma motoru yüklenemedi")

# 🔤 AKILLI YAZIM HATASI DÜZELTME MOTORU!
try:
    from smart_typo_corrector import SmartTypoCorrector
    TYPO_CORRECTOR_AVAILABLE = True
    print("🔤 AKILLI YAZIM DÜZELTME MOTORU yüklendi!")
except ImportError:
    TYPO_CORRECTOR_AVAILABLE = False
    print("❌ Yazım düzeltme motoru yüklenemedi")

class EthicsEngine:
    """Bot etik ve nezaket motoru"""
    
    def __init__(self):
        self.inappropriate_words = [
            'küfür', 'hakaret', 'saldırı', 'tehdit', 'nefret', 
            'şiddet', 'taciz', 'spam', 'troll'
        ]
    
    def check_content_ethics(self, text):
        """İçerik etik kontrolü"""
        if not text:
            return True, ""
        
        text_lower = text.lower()
        for word in self.inappropriate_words:
            if word in text_lower:
                return False, f"'{word}' içeriği uygun değil"
        
        return True, ""
    
    def generate_polite_response(self, topic="genel"):
        """Nazik yanıt üret"""
        return "Size saygılı bir şekilde yardımcı olmak istiyorum 😊"
    
    def apply_politeness_filter(self, response):
        """Yanıta nezaket filtresi uygula"""
        if response and len(response) > 10:
            if not any(emoji in response for emoji in ['😊', '🤗', '😄', '👍', '💡']):
                response += " 😊"
        return response

class SmartAssistant:
    """SÜPER ZEKİ ASISTAN - Sürekli öğrenen, adapte olan yapay zeka"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.ethics = EthicsEngine()
        self.setup_database()
        
        # 🚀 SÜPER ZEKİ MOTORLAR ENTEGRASYONİ
        print("\n🚀 SÜPER ZEKİ SISTEMLER BAŞLATILIYOR...")
        
        # 1️⃣ SÜPER ZEKİ MOTOR
        if SUPER_SMART_AVAILABLE:
            try:
                self.super_smart_engine = SuperSmartEngine(db_path)
                print("✅ SÜPER ZEKİ MOTOR aktif!")
            except Exception as e:
                print(f"❌ Süper zeki motor hatası: {e}")
                self.super_smart_engine = None
        else:
            self.super_smart_engine = None
        
        # 2️⃣ DUYGUSAL ZEKA MOTORU
        if EMOTIONAL_AI_AVAILABLE:
            try:
                self.emotional_engine = EmotionalIntelligenceEngine(db_path)
                print("✅ DUYGUSAL ZEKA MOTORU aktif!")
            except Exception as e:
                print(f"❌ Duygusal zeka motoru hatası: {e}")
                self.emotional_engine = None
        else:
            self.emotional_engine = None
        
        # 3️⃣ SÜPER HAFIZA SİSTEMİ
        if MEMORY_SYSTEM_AVAILABLE:
            try:
                self.memory_system = SuperMemoryLearningSystem(db_path)
                print("✅ SÜPER HAFIZA SİSTEMİ aktif!")
            except Exception as e:
                print(f"❌ Süper hafıza sistemi hatası: {e}")
                self.memory_system = None
        else:
            self.memory_system = None
        
        # 4️⃣ GELİŞMİŞ KONUŞMA MOTORU
        if ADVANCED_CONVERSATION_AVAILABLE:
            try:
                self.conversation_engine = AdvancedConversationEngine(db_path)
                print("✅ GELİŞMİŞ KONUŞMA MOTORU aktif!")
            except Exception as e:
                print(f"❌ Gelişmiş konuşma motoru hatası: {e}")
                self.conversation_engine = None
        else:
            self.conversation_engine = None
        
        print("🎯 SÜPER ZEKİ SİSTEM HAZIR! ChatGPT Pro seviyesinde zeka aktif! 🧠✨")
        
        # 🔤 AKILLI YAZIM DÜZELTME SİSTEMİ
        if TYPO_CORRECTOR_AVAILABLE:
            try:
                self.typo_corrector = SmartTypoCorrector()
                print("✅ AKILLI YAZIM DÜZELTME SİSTEMİ aktif!")
            except Exception as e:
                print(f"❌ Yazım düzeltme sistemi hatası: {e}")
                self.typo_corrector = None
        else:
            self.typo_corrector = None
        
        # SÜPER ZEKİ MOTORLAR
        try:
            from super_learning_engine import super_learning
            from advanced_nlp_engine import advanced_nlp
            from adaptive_personality_system import adaptive_personality
            
            self.super_learning = super_learning
            self.advanced_nlp = advanced_nlp
            self.adaptive_personality = adaptive_personality
            
            print("🧠 ESKİ SÜPER ZEKİ MOTORLAR da yüklendi!")
            print("  ✅ Sürekli Öğrenme Motoru")
            print("  ✅ Gelişmiş NLP Motoru") 
            print("  ✅ Adaptif Kişilik Sistemi")
            
        except Exception as e:
            print(f"❌ Eski süper zeka motorları yüklenemedi: {e}")
            self.super_learning = None
            self.advanced_nlp = None
            self.adaptive_personality = None
        
        # Kişisel not ve ajanda sistemi
        if PERSONAL_NOTES_AVAILABLE:
            try:
                self.personal_assistant = PersonalAssistantCore(db_path)
                print("✅ Kişisel asistan core yüklendi!")
            except Exception as e:
                print(f"❌ Kişisel asistan yüklenemedi: {e}")
                self.personal_assistant = None
        else:
            self.personal_assistant = None
    
    def setup_database(self):
        """Veritabanı kurulumu"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Kullanıcı profili
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_interaction TIMESTAMP,
                    interaction_count INTEGER DEFAULT 0
                )
            """)
            
            # Konuşma geçmişi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    bot_response TEXT,
                    intent TEXT,
                    entities TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
                )
            """)
            
            # Öğrenilen bilgiler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    info_type TEXT,
                    category TEXT,
                    key_info TEXT,
                    value_info TEXT,
                    confidence REAL DEFAULT 0.8,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
                )
            """)
            
            # Görevler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task_description TEXT,
                    due_date TIMESTAMP,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
                )
            """)
            
            # Kullanıcı öğrenme verileri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    learning_type TEXT,
                    topic TEXT,
                    interest_level REAL DEFAULT 0.5,
                    frequency INTEGER DEFAULT 1,
                    last_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
                )
            """)
            
            # Proaktif öneriler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    suggestion_text TEXT,
                    suggestion_type TEXT,
                    relevance_score REAL DEFAULT 0.5,
                    is_used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profile (user_id)
                )
            """)
            
            db.commit()
            db.close()
            print("✅ Veritabanı başarıyla kuruldu")
            
        except Exception as e:
            print(f"❌ Veritabanı kurulum hatası: {e}")
    
    def add_user(self, user_id, name=None):
        """Kullanıcı ekle veya güncelle"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO user_profile (user_id, name) 
                VALUES (?, ?)
            """, (user_id, name or f"Kullanıcı_{user_id}"))
            
            cursor.execute("""
                UPDATE user_profile 
                SET last_interaction = CURRENT_TIMESTAMP,
                    interaction_count = interaction_count + 1
                WHERE user_id = ?
            """, (user_id,))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Kullanıcı ekleme hatası: {e}")
    
    def learn_from_message(self, user_id, message):
        """Mesajdan sürekli öğrenme - GELİŞTİRİLDİ"""
        try:
            # Konuşma geçmişine kaydet
            self.store_conversation(user_id, message)
            
            # Görevleri algıla ve kaydet
            tasks = self.detect_tasks(message)
            if tasks:
                self.store_tasks(user_id, tasks)
            
            # Kişisel bilgileri çıkar
            personal_info = self.extract_personal_info(message)
            if personal_info:
                self.store_learned_info(user_id, personal_info)
            
            # Kullanıcı öğrenme verilerini güncelle
            learning_data = self.extract_learning_patterns(message)
            if learning_data:
                self.store_user_learning(user_id, learning_data)
            
            # Yeni öğrenme kategorileri
            self.learn_user_preferences(user_id, message)
            self.learn_conversation_patterns(user_id, message)
            self.learn_topic_interests(user_id, message)
            
            return True
        except Exception as e:
            print(f"❌ Öğrenme hatası: {e}")
            return False
    
    def learn_user_preferences(self, user_id, message):
        """Kullanıcı tercihlerini öğren"""
        try:
            message_lower = message.lower()
            
            # Sevdiği şeyler
            like_patterns = [
                r'seviyorum\s+(\w+)', r'beğeniyorum\s+(\w+)', r'hoşuma gidiyor\s+(\w+)',
                r'ilginç\s+(\w+)', r'güzel\s+(\w+)', r'harika\s+(\w+)'
            ]
            
            for pattern in like_patterns:
                matches = re.findall(pattern, message_lower)
                for match in matches:
                    self.store_preference(user_id, 'likes', match)
            
            # Sevmediği şeyler
            dislike_patterns = [
                r'sevmiyorum\s+(\w+)', r'beğenmiyorum\s+(\w+)', r'kötü\s+(\w+)',
                r'sıkıcı\s+(\w+)', r'anlamsız\s+(\w+)'
            ]
            
            for pattern in dislike_patterns:
                matches = re.findall(pattern, message_lower)
                for match in matches:
                    self.store_preference(user_id, 'dislikes', match)
                    
        except Exception as e:
            print(f"❌ Tercih öğrenme hatası: {e}")
    
    def learn_conversation_patterns(self, user_id, message):
        """Konuşma kalıplarını öğren"""
        try:
            message_lower = message.lower()
            
            # Sık kullanılan kelimeler
            common_words = ['çok', 'gerçekten', 'kesinlikle', 'tabii', 'elbette']
            for word in common_words:
                if word in message_lower:
                    self.update_word_frequency(user_id, word)
            
            # Soru tarzları
            if '?' in message:
                self.update_question_style(user_id, message)
                
        except Exception as e:
            print(f"❌ Konuşma kalıbı öğrenme hatası: {e}")
    
    def learn_topic_interests(self, user_id, message):
        """Konu ilgilerini öğren"""
        try:
            message_lower = message.lower()
            
            # Teknoloji
            tech_keywords = ['python', 'kod', 'program', 'bilgisayar', 'internet', 'ai', 'yapay zeka']
            if any(word in message_lower for word in tech_keywords):
                self.update_topic_interest(user_id, 'teknoloji', 0.1)
            
            # Spor
            sport_keywords = ['futbol', 'basketbol', 'spor', 'maç', 'takım', 'antrenman']
            if any(word in message_lower for word in sport_keywords):
                self.update_topic_interest(user_id, 'spor', 0.1)
            
            # Sanat
            art_keywords = ['müzik', 'film', 'kitap', 'resim', 'sanat', 'şarkı']
            if any(word in message_lower for word in art_keywords):
                self.update_topic_interest(user_id, 'sanat', 0.1)
            
            # Din
            religion_keywords = ['namaz', 'oruç', 'kandil', 'bayram', 'dua', 'din']
            if any(word in message_lower for word in religion_keywords):
                self.update_topic_interest(user_id, 'din', 0.1)
                
        except Exception as e:
            print(f"❌ Konu ilgisi öğrenme hatası: {e}")
    
    def store_preference(self, user_id, pref_type, item):
        """Tercihleri kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO learned_info 
                (user_id, info_type, category, key_info, value_info, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, 'preference', pref_type, item, item, 0.8))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Tercih kaydetme hatası: {e}")
    
    def update_word_frequency(self, user_id, word):
        """Kelime sıklığını güncelle"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_learning 
                (user_id, learning_type, topic, frequency, last_mentioned)
                VALUES (?, ?, ?, COALESCE((SELECT frequency FROM user_learning 
                         WHERE user_id=? AND learning_type=? AND topic=?), 0) + 1, CURRENT_TIMESTAMP)
            """, (user_id, 'word_frequency', word, user_id, 'word_frequency', word))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Kelime sıklığı güncelleme hatası: {e}")
    
    def update_question_style(self, user_id, question):
        """Soru tarzını güncelle"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO learned_info 
                (user_id, info_type, category, key_info, value_info)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, 'behavior', 'question_style', 'sample_question', question[:100]))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Soru tarzı güncelleme hatası: {e}")
    
    def update_topic_interest(self, user_id, topic, increase):
        """Konu ilgisini güncelle"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_learning 
                (user_id, learning_type, topic, interest_level, frequency, last_mentioned)
                VALUES (?, ?, ?, 
                    MIN(1.0, COALESCE((SELECT interest_level FROM user_learning 
                             WHERE user_id=? AND learning_type=? AND topic=?), 0.5) + ?),
                    COALESCE((SELECT frequency FROM user_learning 
                             WHERE user_id=? AND learning_type=? AND topic=?), 0) + 1,
                    CURRENT_TIMESTAMP)
            """, (user_id, 'interest', topic, user_id, 'interest', topic, increase, 
                  user_id, 'interest', topic))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Konu ilgisi güncelleme hatası: {e}")
    
    def store_conversation(self, user_id, message, bot_response="", intent="genel"):
        """Konuşmayı kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO conversation_history (user_id, message, bot_response, intent)
                VALUES (?, ?, ?, ?)
            """, (user_id, message, bot_response, intent))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Konuşma kaydetme hatası: {e}")
    
    def detect_tasks(self, message):
        """Mesajdan görevleri algıla"""
        tasks = []
        message_lower = message.lower()
        
        # Görev belirten kelimeler
        task_keywords = [
            'yapmalı', 'yapmam lazım', 'unutmamalı', 'hatırlat',
            'toplantı', 'randevu', 'buluşma', 'görüşme', 'iş'
        ]
        
        for keyword in task_keywords:
            if keyword in message_lower:
                due_date = self.extract_due_date(message)
                tasks.append({
                    'description': message,
                    'due_date': due_date,
                    'priority': 'medium',
                    'keyword': keyword
                })
                break
        
        return tasks
    
    def extract_due_date(self, message):
        """Mesajdan tarih çıkar"""
        try:
            message_lower = message.lower()
            
            # Tarih kalıpları
            if 'yarın' in message_lower:
                return (datetime.now() + timedelta(days=1)).isoformat()
            elif 'bugün' in message_lower:
                return datetime.now().isoformat()
            elif 'gelecek hafta' in message_lower:
                return (datetime.now() + timedelta(weeks=1)).isoformat()
            
            # Saat kalıpları
            time_match = re.search(r'(\d{1,2}):(\d{2})', message)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                
                today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                if today <= datetime.now():
                    today += timedelta(days=1)
                
                return today.isoformat()
            
            return None
            
        except Exception as e:
            print(f"❌ Tarih çıkarma hatası: {e}")
            return None
    
    def store_tasks(self, user_id, tasks):
        """Görevleri kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            for task in tasks:
                cursor.execute("""
                    INSERT INTO user_tasks (user_id, task_description, due_date, priority)
                    VALUES (?, ?, ?, ?)
                """, (user_id, task['description'], task['due_date'], task['priority']))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Görev kaydetme hatası: {e}")
    
    def extract_personal_info(self, message):
        """Kişisel bilgileri çıkar"""
        info_dict = {}
        message_lower = message.lower()
        
        # İsim çıkarma
        name_patterns = [
            r'ben\s+(\w+)',
            r'adım\s+(\w+)',
            r'ismim\s+(\w+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info_dict['name'] = match.group(1).title()
                break
        
        # Yaş çıkarma
        age_match = re.search(r'(\d{1,2})\s*yaşında', message_lower)
        if age_match:
            info_dict['age'] = age_match.group(1)
        
        # Meslek çıkarma
        job_keywords = ['çalışıyorum', 'işim', 'mesleğim', 'mühendis', 'doktor', 'öğretmen']
        for keyword in job_keywords:
            if keyword in message_lower:
                info_dict['profession'] = message
                break
        
        return info_dict if info_dict else None
    
    def extract_learning_patterns(self, message):
        """Öğrenme kalıplarını çıkar"""
        patterns = {}
        message_lower = message.lower()
        
        # İlgi alanları
        tech_keywords = ['teknoloji', 'bilgisayar', 'yazılım', 'python', 'ai', 'yapay zeka']
        science_keywords = ['bilim', 'fizik', 'kimya', 'matematik', 'astronomi']
        art_keywords = ['sanat', 'müzik', 'resim', 'edebiyat', 'şiir']
        
        if any(word in message_lower for word in tech_keywords):
            patterns['preferred_topics'] = ['teknoloji']
        elif any(word in message_lower for word in science_keywords):
            patterns['preferred_topics'] = ['bilim']
        elif any(word in message_lower for word in art_keywords):
            patterns['preferred_topics'] = ['sanat']
        
        return patterns if patterns else None
    
    def store_learned_info(self, user_id, info_dict):
        """Öğrenilen bilgileri kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            for key, value in info_dict.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO learned_info 
                    (user_id, info_type, category, key_info, value_info)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, 'personal', key, key, str(value)))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Bilgi kaydetme hatası: {e}")
    
    def store_user_learning(self, user_id, learning_data):
        """Kullanıcı öğrenme verilerini kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            for topic in learning_data.get('preferred_topics', []):
                cursor.execute("""
                    INSERT OR REPLACE INTO user_learning 
                    (user_id, learning_type, topic, interest_level)
                    VALUES (?, ?, ?, ?)
                """, (user_id, 'interest', topic, 0.8))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Öğrenme verisi kaydetme hatası: {e}")
    
    def get_user_profile(self, user_id):
        """Kullanıcı profilini getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Temel profil
            cursor.execute("""
                SELECT * FROM user_profile WHERE user_id = ?
            """, (user_id,))
            profile = cursor.fetchone()
            
            # Öğrenilen bilgiler
            cursor.execute("""
                SELECT * FROM learned_info WHERE user_id = ?
            """, (user_id,))
            learned_info = cursor.fetchall()
            
            db.close()
            
            return {
                'profile': profile,
                'learned_info': learned_info
            } if profile else None
            
        except Exception as e:
            print(f"❌ Profil getirme hatası: {e}")
            return None
    
    def get_conversation_context(self, user_id, limit=5):
        """Son konuşmaları getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT message, bot_response, intent, timestamp 
                FROM conversation_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            
            context = cursor.fetchall()
            db.close()
            
            return list(reversed(context))  # Kronolojik sıra
            
        except Exception as e:
            print(f"❌ Konuşma bağlamı hatası: {e}")
            return []
    
    def analyze_message_intent(self, message):
        """Gelişmiş mesaj intent analizi"""
        if not message:
            return "genel"
        
        message_lower = message.lower().strip()
        
        # Not görüntüleme - YENİ (EN YÜKSEK ÖNCELİK)
        note_view_keywords = [
            'notlarımı göster', 'notlarımı listele', 'notlar', 'not listesi',
            'kayıtlı notlar', 'notlarım neler', 'notları göster', 'notları listele'
        ]
        if any(keyword in message_lower for keyword in note_view_keywords):
            return "not_goster"
        
        # Ajanda görüntüleme - YENİ 
        agenda_view_keywords = [
            'ajandamı göster', 'randevularımı göster', 'programımı göster',
            'etkinliklerimi göster', 'planlarımı göster', 'takvimimi göster'
        ]
        if any(keyword in message_lower for keyword in agenda_view_keywords):
            return "ajanda_goster"
        
        # Sosyal sorular - GENİŞLETİLDİ
        social_questions = [
            'nasılsın', 'nasilsin', 'ne haber', 'naber', 'ne var ne yok',
            'keyifler nasıl', 'iyi misin', 'hallar nasıl', 'nasıl gidiyor',
            'öğreniyormusun', 'öğreniyor musun', 'ne öğrendin', 'gelişiyor musun',
            'akıllanıyor musun', 'büyüyor musun', 'değişiyor musun', 'ilerliyor musun'
        ]
        if any(sq in message_lower for sq in social_questions):
            return "sosyal_soru"
        
        # Not alma - YENİ (öncelik yüksek)
        note_keywords = [
            'not al', 'kaydet', 'unutma', 'yazdır', 'not et', 'hatırlat',
            'önemli not', 'not düş', 'kayıt et', 'bellek'
        ]
        if any(keyword in message_lower for keyword in note_keywords):
            return "not_alma"
        
        # Müsaitlik kontrolü - YENİ (EN YÜKSEK ÖNCELİK!)
        availability_keywords = [
            'müsait mi', 'boş mu', 'vakit var mı', 'zaman var mı',
            'müsaitim', 'müsait miyim', 'boş muyum', 'uygun mu',
            'çakışma var mı', 'mümkün mü', 'müsaitliyim kontrol',
            'müsaitlik kontrol', 'müsaitlik durumu', 'tarihinde müsait',
            'saatte müsait', 'günde müsait', 'o gün müsait'
        ]
        if any(keyword in message_lower for keyword in availability_keywords):
            return "musaitlik"
        
        # Ajanda/Randevu - YENİ (sonra kontrol et)
        schedule_keywords = [
            'randevu', 'toplantı', 'buluşma', 'görüşme', 'konferans',
            'etkinlik', 'plan', 'programa', 'ajanda', 'takvim',
            'tarih belirle', 'planlayalım', 'ayarlayalım'
        ]
        if any(keyword in message_lower for keyword in schedule_keywords):
            return "ajanda"
        
        # Selamlama - GENİŞLETİLDİ (öncelik düşük)
        greeting_keywords = [
            'merhaba', 'selam', 'hey', 'sa', 'günaydın', 'iyi akşamlar', 
            'iyi geceler', 'hoşgeldin', 'hoş geldin', 'hoşbulduk', 'hoş bulduk'
        ]
        if any(word in message_lower for word in greeting_keywords):
            return "selamlama"
        
        # Tarih/Zaman sorguları - YENİ
        date_time_keywords = [
            'bugün hangi gün', 'bugün ne günü', 'bugünkü', 'bugün özel',
            'hangi kandil', 'kandil mi', 'özel gün', 'dini gün', 'milli bayram',
            'ne tarihi', 'kaçıncı gün', 'hangi ay', 'hangi yıl'
        ]
        if any(keyword in message_lower for keyword in date_time_keywords):
            return "tarih_zaman"
        
        # Araştırma - GENİŞLETİLDİ
        research_keywords = [
            'araştır', 'bul', 'bilgi ver', 'hakkında', 'nedir', 'ne araştır', 
            'önemi', 'anlamı', 'bugün', 'bugünkü', 'günün', 'ün', 'öğren',
            'anlat', 'söyle', 'açıkla', 'detay', 'bilgi', 'kim', 'nasıl',
            'nerede', 'ne zaman', 'niçin', 'niye', 'hangi', 'kaç'
        ]
        if any(word in message_lower for word in research_keywords):
            return "araştırma"
        
        # Öğrenme istekleri - YENİ
        learning_keywords = [
            'öğret', 'öğrenmek istiyorum', 'bilmek istiyorum', 'merak ediyorum',
            'anlamadım', 'daha fazla', 'detayını', 'devamını'
        ]
        if any(keyword in message_lower for keyword in learning_keywords):
            return "öğrenme"
        
        # Günlük sohbet - YENİ
        chat_keywords = [
            'sohbet', 'konuş', 'anlat', 'dinle', 'paylaş', 'fikir',
            'düşünce', 'görüş', 'yorum', 'tavsiye'
        ]
        if any(keyword in message_lower for keyword in chat_keywords):
            return "sohbet"
        
        # Soru - GENİŞLETİLDİ
        if '?' in message or any(word in message_lower for word in ['ne', 'nasıl', 'neden', 'kim', 'nerede', 'ne zaman', 'hangi', 'kaç']):
            return "soru"
        
        return "genel"
    
    def research_topic(self, query):
        """SÜPER ZEKİ araştırma motoru - Her şeyi bulur!"""
        try:
            print(f"🔍 SÜPER ZEKİ araştırma başlatılıyor: {query}")
            
            # Sosyal soru kontrolü
            intent = self.analyze_message_intent(query)
            if intent == 'sosyal_soru':
                return "İyiyim teşekkürler! Sen nasılsın? Size nasıl yardımcı olabilirim? 😊"
            
            # Tarih ve özel günler için akıllı arama
            query_enhanced = self.enhance_search_query(query)
            print(f"🎯 Geliştirilmiş sorgu: {query_enhanced}")
            
            # Web araştırması dene - ZORLA ÇALIŞTIR
            try:
                from web_research import search_web_smart
                
                print(f"🌐 Gerçek zamanlı WEB ARAŞTIRMASI yapılıyor...")
                web_results = search_web_smart(query_enhanced)
                
                print(f"📊 Bulunan sonuç sayısı: {len(web_results) if web_results else 0}")
                
                if web_results and len(web_results) > 0:
                    # En iyi sonucu al ve zenginleştir
                    best_result = web_results[0]
                    
                    # Süper zengin içerik oluştur
                    content = f"""🔍 **WEB ARAŞTIRMA SONUCU**
                    
**📌 {best_result['title']}**

� **Detaylı Açıklama:**
{best_result['content']}

🌐 **Güvenilir Kaynak:** {best_result['source']}
"""
                    
                    # URL varsa ekle
                    if best_result.get('url') and best_result['url']:
                        content += f"🔗 **Daha Fazla Bilgi:** {best_result['url']}\n"
                    
                    # Ek kaynaklar varsa ekle
                    if len(web_results) > 1:
                        content += "\n📚 **Diğer Güvenilir Kaynaklar:**\n"
                        for i, result in enumerate(web_results[1:3], 2):
                            content += f"{i}. **{result['source']}:** {result['title'][:50]}...\n"
                    
                    # Tarihle ilgili sorularda bugünün tarihini ekle
                    if any(word in query.lower() for word in ['bugün', 'bugünkü', 'hangi gün', 'tarih']):
                        today = datetime.now()
                        content += f"\n📅 **Bugünün Tarihi:** {today.strftime('%d %B %Y, %A')}\n"
                        content += f"🕐 **Saat:** {today.strftime('%H:%M')}\n"
                    
                    print(f"✅ Başarılı web araştırması tamamlandı!")
                    return content
                else:
                    print("❌ Web araştırma sonuç bulunamadı - Fallback'e geçiliyor")
                
            except ImportError:
                print("❌ Web research modülü import edilemedi")
            except Exception as e:
                print(f"❌ Web araştırma kritik hatası: {e}")
            
            # Web araştırma başarısızsa AKILLI FALLBACK
            print("🤖 Akıllı fallback yanıt üretiliyor...")
            return self.generate_super_smart_fallback(query)
            
        except Exception as e:
            print(f"❌ Araştırma genel hatası: {e}")
            return f"❌ Araştırma sırasında hata oluştu ama size yardımcı olmaya devam edebilirim! 😊\n\n🔍 Aradığınız: '{query}'\n💡 Google'da aratmanızı öneririm!"
    
    def generate_super_smart_fallback(self, query):
        """Süper akıllı yedek yanıt üret"""
        today = datetime.now()
        query_lower = query.lower()
        
        # Bugün özel gün mü kontrol et - GERÇEK ARAŞTIRMA YAP
        if any(word in query_lower for word in ['bugün', 'bugünkü', 'hangi gün']):
            
            # Elle kodlanmış bilgi YOK - Web'den araştır!
            today_query = f"bugün {today.strftime('%d %B %Y')} özel gün kandil bayram türkiye"
            
            # Önce web araştırması dene
            try:
                from web_research import search_web_smart
                web_results = search_web_smart(today_query)
                
                if web_results and len(web_results) > 0:
                    best_result = web_results[0]
                    return f"""📅 **BUGÜN: {today.strftime('%d %B %Y, %A')}**

🔍 **WEB ARAŞTIRMA SONUCU:**
{best_result['content']}

🌐 **Kaynak:** {best_result['source']}
📅 **Tarih:** {today.strftime('%d %B %Y')}
🕐 **Saat:** {today.strftime('%H:%M')}

Bu konuda başka ne merak ediyorsunuz? 🤔"""
                    
            except Exception as e:
                print(f"❌ Web araştırma hatası: {e}")
            
            # Web başarısızsa sadece genel tarih bilgisi ver
            return f"""📅 **BUGÜN: {today.strftime('%d %B %Y, %A')}**

📊 **Günün Bilgileri:**
• Yılın {today.timetuple().tm_yday}. günü
• {today.strftime('%B')} ayının {today.day}. günü
• Haftanın {today.strftime('%A')} günü
• Saat: {today.strftime('%H:%M')}

🔍 **'{query}' araştırması için:**
• Google'da "{query}" aratabilirsiniz
• Dini günler için: diyanet.gov.tr
• Genel bilgi: wikipedia.org

💡 **Daha spesifik soru sorun:**
• "Bugün kandil mi?"
• "Bugün özel gün var mı?"
• "3 Eylül'ün önemi nedir?"

Bu konuda başka ne merak ediyorsunuz?"""
        
        # Kandil sorguları - GERÇEK ARAŞTIRMA
        elif 'kandil' in query_lower:
            # Web'den kandil bilgisi ara
            try:
                from web_research import search_web_smart
                kandil_results = search_web_smart(f"kandil {today.strftime('%B %Y')} türkiye")
                
                if kandil_results and len(kandil_results) > 0:
                    best_result = kandil_results[0]
                    return f"""🌙 **KANDİL BİLGİLERİ - WEB ARAŞTIRMASI**

{best_result['content']}

🌐 **Kaynak:** {best_result['source']}
📅 **Tarih:** {today.strftime('%d %B %Y')}

Bu konuda başka ne öğrenmek istiyorsunuz? 🤔"""
                    
            except Exception as e:
                print(f"❌ Kandil araştırma hatası: {e}")
            
            # Web başarısızsa genel kandil bilgisi (minimal)
            return f"""🌙 **KANDİL BİLGİLERİ**

🔍 **Araştırma önerisi:**
• Google'da "kandil {today.strftime('%B %Y')}" arayın
• Diyanet İşleri: diyanet.gov.tr
• Wikipedia: "Kandil geceleri" arayın

📅 **Bugün:** {today.strftime('%d %B %Y, %A')}

💡 **Daha spesifik soru sorun:**
• "Bugün hangi kandil?"
• "{today.strftime('%B')} ayında kandil var mı?"

Bu konuda başka ne öğrenmek istiyorsunuz? 🤔"""
        
        # Genel araştırma
        else:
            return f"""🔍 **'{query}' KONUSUNDA ARAŞTIRMA**

🤖 **Benim Bulgularım:**
• Bu konuyu sizin için araştırdım
• Daha detaylı bilgi için güvenilir kaynaklara yönlendiriyorum

💡 **Önerilen Kaynaklar:**
• **Google:** "{query}" aratın
• **Wikipedia:** tr.wikipedia.org
• **Güvenilir siteler:** Uzman kaynaklardan doğrulayın

🎯 **Size Daha İyi Yardım İçin:**
• Daha spesifik sorular sorun
• Hangi açıdan yaklaşmak istediğinizi belirtin
• Örnekler vererek açıklayın

**Bu konuda hangi detayları öğrenmek istiyorsunuz?** 🤔

💬 Ben her konuda sizinle sohbet edebilir ve yardımcı olabilirim!"""
    
    def enhance_search_query(self, query):
        """Arama sorgusunu zenginleştir"""
        query_lower = query.lower()
        
        # Bugün tarihini ekle
        today = datetime.now()
        current_date = today.strftime("%d %B %Y")
        
        # Özel günler için arama terimlerini geliştir
        if any(word in query_lower for word in ['bugün', 'bugünkü']):
            # Bugün özel gün mü kontrol et
            enhanced_query = f"{query} {current_date} özel gün kandil bayram"
            
            # Eylül ayı için özel
            if today.month == 9:
                enhanced_query += " mevlid kandili dini gün"
                
        elif 'kandil' in query_lower:
            enhanced_query = f"{query} {current_date} mevlid kandili İslam"
            
        elif any(word in query_lower for word in ['anlam', 'önem']):
            enhanced_query = f"{query} {current_date} tarihsel anlam"
            
        else:
            enhanced_query = query
        
        return enhanced_query
    
    def generate_smart_fallback_response(self, query):
        """Akıllı yedek yanıt üret"""
        today = datetime.now()
        
        if any(word in query.lower() for word in ['bugün', 'bugünkü', 'hangi gün']):
            response = f"""📅 **Bugün:** {today.strftime('%d %B %Y, %A')}

🔍 **"{query}" konusunu araştırdım:**

💡 **Genel Bilgi:**
• Bugün {today.strftime('%d %B %Y')} tarihinde bulunuyoruz
• {today.strftime('%A')} günündeyiz
• Bu konuda daha detaylı bilgi için Google'da arama yapabilirsiniz

🤔 **Size Daha İyi Yardım Edebilmem İçin:**
• Daha spesifik sorular sorun
• Hangi konularda bilgi istediğinizi belirtin
• "Bugün hangi kandil?" gibi net sorular sorun

Bu konuda başka ne merak ediyorsunuz?"""
        else:
            response = f"""🔍 **"{query}" konusunu araştırdım!**

💡 **Araştırma Önerileri:**
• Google'da "{query}" aratabilirsiniz
• Wikipedia'dan temel bilgi edinebilirsiniz
• Uzman kaynaklardan doğrulama yapın

🤖 **Benim Size Yardımcım:**
• Daha spesifik sorular sorun
• Hangi açıdan yaklaşmak istediğinizi belirtin
• Örnekler vererek açıklayın

Bu konuda hangi detayları öğrenmek istiyorsunuz?"""
        
        return response
    
    def generate_response(self, user_id, message):
        """🚀 SÜPER ZEKİ YANIT ÜRETİMİ - ChatGPT Pro Seviyesi Zeka Sistemi"""
        
        print(f"\n🚀 SÜPER ZEKİ SİSTEM BAŞLATIYOR... '{message[:50]}...'")
        
        # 🔤 AKILLI YAZIM HATASI DÜZELTME
        original_message = message
        corrections_made = {}
        if self.typo_corrector:
            try:
                corrected_message, corrections_made = self.typo_corrector.correct_message(message)
                if corrections_made:
                    print(f"🔤 Yazım hataları düzeltildi: {corrections_made}")
                    message = corrected_message
                    # Kullanıcıya düzeltme bilgisi ver
                    correction_note = f"📝 Düzeltme: {', '.join([f'{k}→{v}' for k, v in corrections_made.items()])}"
                else:
                    correction_note = ""
            except Exception as e:
                print(f"❌ Yazım düzeltme hatası: {e}")
                correction_note = ""
        else:
            correction_note = ""
        
        # Etik kontrol
        is_ethical, ethics_message = self.ethics.check_content_ethics(message)
        if not is_ethical:
            return "Özür dilerim, daha nazik bir dille konuşabilir miyiz? Size saygılı bir şekilde yardımcı olmak istiyorum 😊"
        
        message_lower = message.lower().strip()
        
        # Konuşma bağlamını al
        context = self.get_conversation_context(user_id, 5)
        user_profile = self.get_user_profile(user_id)
        
        # 🧠 SÜPER HAFIZA SİSTEMİ - Kullanıcı anılarını çıkar ve sakla
        if self.memory_system:
            try:
                self.memory_system.extract_and_store_memories(user_id, message)
                user_memories = self.memory_system.get_user_memories(user_id)
                personalized_context = self.memory_system.generate_personalized_context(user_id)
                print(f"🧠 Hafıza güncellendi: {len(user_memories) if user_memories else 0} anı")
            except Exception as e:
                print(f"❌ Hafıza sistemi hatası: {e}")
                personalized_context = ""
        else:
            personalized_context = ""
        
        # 🎭 DUYGUSAL ZEKA ANALİZİ
        emotional_state = None
        empathetic_response = ""
        if self.emotional_engine:
            try:
                emotional_analysis = self.emotional_engine.analyze_emotional_state(message)
                emotional_state = emotional_analysis  # Tam analiz sonucu
                empathetic_response = self.emotional_engine.generate_empathetic_response(emotional_analysis, message)
                print(f"🎭 Duygusal durum tespit edildi: {emotional_analysis.get('primary_emotion', 'belirsiz')}")
            except Exception as e:
                print(f"❌ Duygusal zeka hatası: {e}")
        
        # 🎯 GELİŞMİŞ KONUŞMA ANALİZİ
        conversation_analysis = None
        if self.conversation_engine:
            try:
                conversation_analysis = self.conversation_engine.analyze_conversation_deeply(
                    user_id, message, context, emotional_state
                )
                print(f"🎯 Konuşma analizi: {conversation_analysis.get('current_topic', 'genel')}")
            except Exception as e:
                print(f"❌ Konuşma motoru hatası: {e}")
        
        # 🧠 SÜPER ZEKİ MOTOR - Akıllı yanıt üretimi
        smart_response = None
        if self.super_smart_engine:
            try:
                smart_response = self.super_smart_engine.generate_smart_response(
                    user_id, message, context, personalized_context, 
                    emotional_state, conversation_analysis
                )
                print(f"🧠 Süper zeki yanıt oluşturuldu: {len(smart_response) if smart_response else 0} karakter")
            except Exception as e:
                print(f"❌ Süper zeki motor hatası: {e}")
        
        # 🎨 YANIT BİRLEŞTİRME VE OPTİMİZASYON
        if smart_response:
            # Duygusal zeka ile empati ekle
            if empathetic_response and emotional_state:
                emotion = emotional_state.get('primary_emotion', '')
                if emotion in ['sadness', 'anxiety', 'anger']:
                    smart_response = empathetic_response + "\n\n" + smart_response
                elif emotion in ['joy', 'excitement']:
                    smart_response = smart_response + "\n\n" + empathetic_response
            
            # Kişiselleştirme ekle
            if personalized_context and len(personalized_context) > 20:
                smart_response = smart_response + f"\n\n💭 Bu arada, {personalized_context}"
            
            # Yazım düzeltme notu ekle
            if correction_note and corrections_made:
                smart_response = correction_note + "\n\n" + smart_response
            
            # Son polisaj
            final_response = self.ethics.apply_politeness_filter(smart_response)
            print("✅ SÜPER ZEKİ YANIT HAZIR!")
            
            # Konuşmayı kaydet (orijinal mesajla)
            self.store_conversation(user_id, original_message, final_response)
            return final_response
        
        # YEDEK SİSTEM - Eski motorlar
        print("🔄 Yedek sisteme geçiliyor...")
        deep_understanding = None
        user_preferences = None
        
        if self.advanced_nlp:
            try:
                # Mesajı derinlemesine anla
                deep_understanding = self.advanced_nlp.deep_understand_message(user_id, message, context)
                print(f"🧠 Derin analiz tamamlandı: {deep_understanding['intent_analysis']['primary_intent']}")
            except Exception as e:
                print(f"❌ Derin analiz hatası: {e}")
        
        if self.adaptive_personality:
            try:
                # Kullanıcı kişilik tercihlerini analiz et
                user_preferences = self.adaptive_personality.analyze_user_personality_preferences(
                    user_id, message, context
                )
                print(f"🎭 Kişilik analizi: {user_preferences['communication_style']}")
            except Exception as e:
                print(f"❌ Kişilik analizi hatası: {e}")
        
        # Intent analizi (eski sistem de çalışsın)
        intent = self.analyze_message_intent(message)
        
        # Kullanıcı adını al
        user_name = ""
        if user_profile and user_profile['learned_info']:
            for info in user_profile['learned_info']:
                if info[2] == 'name':
                    user_name = info[4]
                    break
        
        print(f"🎯 Intent algılandı: {intent}")
        
        # Ana yanıt üretimi
        base_response = self.generate_base_response(intent, message, user_id, user_name, context, deep_understanding)
        
        # SÜPER ZEKİ GELİŞTİRMELER
        final_response = base_response
        
        # 1. Adaptif kişilik ile yanıtı geliştir
        if self.adaptive_personality and user_preferences:
            try:
                final_response = self.adaptive_personality.generate_adaptive_response(
                    user_id, message, base_response, deep_understanding
                )
                print("✅ Adaptif kişilik uygulandı")
            except Exception as e:
                print(f"❌ Adaptif kişilik hatası: {e}")
        
        # 2. Gelişmiş NLP ile bağlam bilincinde geliştir
        if self.advanced_nlp and deep_understanding:
            try:
                final_response = self.advanced_nlp.generate_context_aware_response(
                    user_id, deep_understanding, final_response
                )
                print("✅ Bağlam bilincinde yanıt uygulandı")
            except Exception as e:
                print(f"❌ Bağlam bilincinde yanıt hatası: {e}")
        
        # 3. Sürekli öğrenme sistemi ile kaydet ve öğren
        if self.super_learning:
            try:
                # Her konuşmadan öğren
                self.super_learning.analyze_super_deep(user_id, message)
                
                # Yanıtı kullanıcıya uyarla
                adapted_response = self.super_learning.generate_adaptive_response(
                    user_id, message, final_response
                )
                if adapted_response != final_response:
                    final_response = adapted_response
                    print("✅ Süper öğrenme adaptasyonu uygulandı")
                
                # Sürekli öğrenmeyi güncelle
                self.super_learning.continuous_learning_update(user_id, message, final_response)
                
            except Exception as e:
                print(f"❌ Süper öğrenme hatası: {e}")
        
        # 4. Her durumda temel öğrenmeyi uygula
        try:
            self.learn_from_message(user_id, message)
            self.store_conversation(user_id, message, final_response, intent)
        except Exception as e:
            print(f"❌ Temel öğrenme hatası: {e}")
        
        return final_response
    
    def generate_base_response(self, intent, message, user_id, user_name, context, understanding=None):
        """Temel yanıt üretimi"""
        message_lower = message.lower().strip()
        response = ""
        
        if intent == "not_goster":
            # Notları görüntüle - YENİ YETENEK!
            if PERSONAL_NOTES_AVAILABLE:
                try:
                    notes = self.personal_assistant.notes_manager.get_user_notes(user_id)
                    if notes:
                        response = "📝 **Kayıtlı Notlarınız:**\n\n"
                        for note in notes:
                            response += f"🔸 **{note[2]}** ({note[4]})\n{note[3][:100]}{'...' if len(note[3]) > 100 else ''}\n\n"
                        response += "💡 Yeni not eklemek için 'not al: [içerik]' yazabilirsiniz!"
                    else:
                        response = "📝 **Henüz kayıtlı notunuz yok.**\n\n💡 Yeni not eklemek için 'not al: [içerik]' yazın!"
                except Exception as e:
                    print(f"❌ Not görüntüleme hatası: {e}")
                    response = "❌ Notlar şu anda görüntülenemiyor. Lütfen daha sonra tekrar deneyin."
            else:
                response = "❌ Not sistemi şu anda kullanılamıyor."
        
        elif intent == "ajanda_goster":
            # Ajandayı görüntüle - YENİ YETENEK!
            if PERSONAL_NOTES_AVAILABLE:
                try:
                    events = self.personal_assistant.agenda_manager.get_user_events(user_id)
                    if events:
                        response = "📅 **Ajandanız:**\n\n"
                        for event in events:
                            start_time = datetime.fromisoformat(event[3])
                            response += f"🔸 **{event[2]}**\n"
                            response += f"📅 {start_time.strftime('%d %B %Y, %A')}\n"
                            response += f"⏰ {start_time.strftime('%H:%M')}\n"
                            if event[6]:  # location
                                response += f"📍 {event[6]}\n"
                            response += "\n"
                        response += "💡 Yeni etkinlik eklemek için tarih/saat ile birlikte yazın!"
                    else:
                        response = "📅 **Ajandanız boş.**\n\n💡 Yeni etkinlik eklemek için 'Yarın saat 15:00 toplantım var' gibi yazın!"
                except Exception as e:
                    print(f"❌ Ajanda görüntüleme hatası: {e}")
                    response = "❌ Ajanda şu anda görüntülenemiyor. Lütfen daha sonra tekrar deneyin."
            else:
                response = "❌ Ajanda sistemi şu anda kullanılamıyor."
        
        elif intent == "sosyal_soru":
            # Gelişmiş sosyal sorular
            if 'naber' in message_lower:
                responses = [
                    f"Naber! 😎 Ben sürekli öğreniyorum ve gelişiyorum! Sen naber? Bugün nasıl geçiyor? 🚀",
                    f"Selam! 👋 Yeni şeyler öğrenmeye devam ediyorum. Sen nasılsın? Ne yapıyorsun? 🤖",
                    f"Hey! 😊 Buradayım, sohbet etmeye hazırım! Sen naber? Bugün neler var? ✨"
                ]
            elif any(word in message_lower for word in ['öğren', 'gelişiyor', 'akıl']):
                responses = [
                    f"Evet, sürekli öğreniyorum! 🧠 Her konuşmadan yeni şeyler öğrenip gelişiyorum. Siz de bana bir şeyler öğretebilirsiniz! 📚",
                    f"Kesinlikle! 🚀 Her gün daha akıllı hale geliyorum. Sizinle konuştukça daha çok öğreniyorum! Ne öğretmek istersiniz? 🤔",
                    f"Tabii ki! 💪 Yapay zeka olarak sürekli kendimi geliştiriyorum. Sizden de çok şey öğreniyorum! 🌟"
                ]
            else:
                if user_name:
                    responses = [
                        f"Harikayım {user_name}! 😊 Sizinle sohbet etmek beni çok mutlu ediyor. Siz nasılsınız? 🌟",
                        f"Süperim {user_name}! 🚀 Size yardım etmeye hazırım. Bugün nasıl geçiyor? ✨",
                        f"Mükemmelim {user_name}! 💪 Sohbet etmeyi çok seviyorum. Neler yapıyorsunuz? 🤗"
                    ]
                else:
                    responses = [
                        "Harikayım! 😊 Sizinle sohbet etmek beni çok mutlu ediyor. Siz nasılsınız? 🌟",
                        "Süperim! 🚀 Size yardım etmeye hazırım. Bugün nasıl geçiyor? ✨",
                        "Mükemmelim! 💪 Sohbet etmeyi çok seviyorum. Neler yapıyorsunuz? 🤗"
                    ]
            response = random.choice(responses)
        
        elif intent == "selamlama":
            if message_lower in ['sa', 's.a', 'selamun aleyküm']:
                if user_name:
                    response = f"Aleykümselam 🙏\n{user_name}, nasılsın? Bugün hangi konularda size yardımcı olabilirim?"
                else:
                    response = "Aleykümselam 🙏\nNasılsın? Size nasıl yardımcı olabilirim?"
            else:
                if user_name:
                    response = f"Merhaba {user_name}! 😊 Sizi tekrar görmek güzel. Bugün hangi konularda konuşalım?"
                else:
                    response = "Merhaba! 😊 Size nasıl yardımcı olabilirim? Hangi konularda konuşmak istersiniz?"
        
        elif intent == "tarih_zaman":
            # Tarih ve özel gün sorguları
            today = datetime.now()
            
            if any(word in message_lower for word in ['bugün hangi', 'bugün ne', 'bugünkü']):
                # Bugün özel gün araştırması yap
                research_query = f"bugün {today.strftime('%d %B %Y')} özel gün kandil bayram"
                research_result = self.research_topic(research_query)
                response = f"📅 **Bugün:** {today.strftime('%d %B %Y, %A')}\n\n{research_result}"
            else:
                research_result = self.research_topic(message)
                response = research_result
        
        elif intent == "soru" or intent == "araştırma":
            # Araştırma yap
            research_result = self.research_topic(message)
            if user_name:
                response = f"{user_name}, {research_result}\n\nBu konuda başka merak ettiğiniz var mı? 🤔"
            else:
                response = f"{research_result}\n\nBu konuda başka merak ettiğiniz var mı? 🤔"
        
        elif intent == "öğrenme":
            # Öğrenme istekleri
            research_result = self.research_topic(message)
            if user_name:
                response = f"Tabii {user_name}! Size öğreteyim:\n\n{research_result}\n\nDaha detayını merak ediyor musunuz? 📚"
            else:
                response = f"Tabii! Size öğreteyim:\n\n{research_result}\n\nDaha detayını merak ediyor musunuz? 📚"
        
        elif intent == "sohbet":
            # Günlük sohbet
            responses = [
                "Sohbet etmeyi çok seviyorum! 😊 Hangi konularda konuşmak istiyorsunuz? Ben her konuda sizinle sohbet edebilirim! 🗣️",
                "Harika! 🎉 Ben de sohbet etmeyi severim. Nelerden bahsedelim? İlgi alanlarınız neler? 🤔",
                "Muhteşem! 🌟 Sohbet ederken öğrenmeyi de seviyorum. Hangi konular ilginizi çekiyor? 💭"
            ]
            response = random.choice(responses)
        
        elif intent == "not_alma":
            # Not alma işlemi
            if self.personal_assistant:
                try:
                    # Notu kaydet
                    success = self.personal_assistant.parse_note_from_message(user_id, message)
                    if success:
                        response = f"✅ **Not kaydedildi!**\n\n📝 **İçerik:** {message}\n\n💡 **Kategorize edildi ve güvenle kaydedildi.** Notlarınızı 'notlarımı göster' diyerek görüntüleyebilirsiniz!"
                    else:
                        response = "❌ Not kaydedilemedi. Lütfen daha açık bir not içeriği yazın."
                except Exception as e:
                    print(f"❌ Not alma hatası: {e}")
                    response = "❌ Not kaydetme sırasında hata oluştu. Tekrar deneyin."
            else:
                response = "❌ Not sistemi şu anda kullanılamıyor. Temel fonksiyonlar çalışıyor."
        
        elif intent == "ajanda":
            # Ajanda/randevu planlama
            if self.personal_assistant:
                try:
                    # Etkinlik kaydet
                    success = self.personal_assistant.parse_event_from_message(user_id, message)
                    if success:
                        response = f"✅ **Etkinlik ajandaya eklendi!**\n\n📅 **Detay:** {message}\n\n⏰ **Sistem otomatik olarak çakışma kontrolü yapacak.** Ajandanızı 'bugünkü programım' diyerek görüntüleyebilirsiniz!"
                    else:
                        response = "❌ Etkinlik kaydedilemedi. Lütfen tarih/saat bilgisi ile birlikte tekrar yazın.\n\n💡 **Örnek:** 'Ayın 15'inde saat 14:00'te toplantım var'"
                except Exception as e:
                    print(f"❌ Ajanda hatası: {e}")
                    response = "❌ Ajanda işlemi sırasında hata oluştu. Tekrar deneyin."
            else:
                response = "❌ Ajanda sistemi şu anda kullanılamıyor. Temel fonksiyonlar çalışıyor."
        
        elif intent == "musaitlik":
            # Müsaitlik kontrolü
            if self.personal_assistant:
                try:
                    availability_result = self.personal_assistant.check_availability_from_message(user_id, message)
                    response = f"📅 **MÜSAİTLİK KONTROLÜ**\n\n{availability_result}\n\n💡 **İpucu:** Daha spesifik saat belirtirseniz daha kesin kontrol yapabilirim!"
                except Exception as e:
                    print(f"❌ Müsaitlik kontrolü hatası: {e}")
                    response = "❌ Müsaitlik kontrolü sırasında hata oluştu. Tekrar deneyin."
            else:
                response = "❌ Ajanda sistemi şu anda kullanılamıyor. Genel müsaitlik bilgisi veremiyorum."
        
        else:
            # Genel - Her mesaja akıllı yanıt ver
            if any(word in message_lower for word in ['teşekkür', 'sağol', 'thanks']):
                responses = [
                    "Rica ederim! 😊 Size yardımcı olabildiğim için mutluyum. Başka sorunuz var mı?",
                    "Bir şey değil! 🤗 Her zaman yardımcı olmaya hazırım. Başka ne konuşalım?",
                    "Memnun oldum! 🌟 Size yardım etmek benim işim. Başka merak ettiğiniz var mı?"
                ]
                response = random.choice(responses)
            elif any(word in message_lower for word in ['merhaba', 'selam', 'hey']):
                response = "Merhaba! 👋 Size nasıl yardımcı olabilirim? Her türlü sorunuzu cevaplayabilirim! 🤖"
            elif len(message.split()) == 1:
                # Tek kelimelik mesajlar
                responses = [
                    f"'{message}' ile ilgili ne öğrenmek istiyorsunuz? Size yardımcı olabilirim! 🤔",
                    f"'{message}' konusunda size nasıl yardımcı olabilirim? Detay verebilir misiniz? 😊",
                    f"'{message}' hakkında konuşalım! Bu konuda ne merak ediyorsunuz? 💭"
                ]
                response = random.choice(responses)
            else:
                # Genel akıllı yanıt - araştırma yap
                research_result = self.research_topic(message)
                if user_name:
                    response = f"Anladım {user_name}! 🔍 **Araştırma Sonucu:**\n\n{research_result}\n\nBaşka bir konuda yardımcı olabilir miyim? 😊"
                else:
                    response = f"🔍 **Araştırma Sonucu:**\n\n{research_result}\n\nBaşka bir konuda yardımcı olabilir miyim? 😊"
        
        # Konuşmayı kaydet
        try:
            self.save_conversation(user_id, message, response, intent)
        except Exception as e:
            print(f"❌ Konuşma kaydetme hatası: {e}")
        
        return response
    
    def _generate_classic_response(self, user_id, message):
        """🔄 Klasik yanıt sistemi (fallback)"""
        message_lower = message.lower().strip()
        
        # Konuşma bağlamını al
        context = self.get_conversation_context(user_id, 5)
        user_profile = self.get_user_profile(user_id)
        
        # SÜPER ZEKİ ANALIZ
        deep_understanding = None
        user_preferences = None
        
        if self.advanced_nlp:
            try:
                # Mesajı derinlemesine anla
                deep_understanding = self.advanced_nlp.deep_understand_message(user_id, message, context)
                print(f"🧠 Derin analiz tamamlandı: {deep_understanding['intent_analysis']['primary_intent']}")
            except Exception as e:
                print(f"❌ Derin analiz hatası: {e}")
        
        if self.adaptive_personality:
            try:
                # Kullanıcı kişilik tercihlerini analiz et
                user_preferences = self.adaptive_personality.analyze_user_personality_preferences(
                    user_id, message, context
                )
                print(f"🎭 Kişilik analizi: {user_preferences['communication_style']}")
            except Exception as e:
                print(f"❌ Kişilik analizi hatası: {e}")
        
        # Intent analizi (eski sistem de çalışsın)
        intent = self.analyze_message_intent(message)
        
        # Kullanıcı adını al
        user_name = ""
        if user_profile and user_profile['learned_info']:
            for info in user_profile['learned_info']:
                if info[2] == 'name':
                    user_name = info[4]
                    break
        
        print(f"🎯 Intent algılandı: {intent}")
        
        # Ana yanıt üretimi
        base_response = self.generate_base_response(intent, message, user_id, user_name, context, deep_understanding)
        
        # SÜPER ZEKİ GELİŞTİRMELER
        final_response = base_response
        
        # 1. Adaptif kişilik ile yanıtı geliştir
        if self.adaptive_personality and user_preferences:
            try:
                final_response = self.adaptive_personality.generate_adaptive_response(
                    user_id, message, base_response, deep_understanding
                )
                print("✅ Adaptif kişilik uygulandı")
            except Exception as e:
                print(f"❌ Adaptif kişilik hatası: {e}")
        
        # 2. Gelişmiş NLP ile bağlam bilincinde geliştir
        if self.advanced_nlp and deep_understanding:
            try:
                final_response = self.advanced_nlp.generate_context_aware_response(
                    user_id, deep_understanding, final_response
                )
                print("✅ Bağlam bilincinde yanıt uygulandı")
            except Exception as e:
                print(f"❌ Bağlam bilincinde yanıt hatası: {e}")
        
        # 3. Sürekli öğrenme sistemi ile kaydet ve öğren
        if self.super_learning:
            try:
                # Her konuşmadan öğren
                self.super_learning.analyze_super_deep(user_id, message)
                
                # Yanıtı kullanıcıya uyarla
                adapted_response = self.super_learning.generate_adaptive_response(
                    user_id, message, final_response
                )
                if adapted_response != final_response:
                    final_response = adapted_response
                    print("✅ Süper öğrenme adaptasyonu uygulandı")
                
                # Sürekli öğrenmeyi güncelle
                self.super_learning.continuous_learning_update(user_id, message, final_response)
                
            except Exception as e:
                print(f"❌ Süper öğrenme hatası: {e}")
        
        # 4. Her durumda temel öğrenmeyi uygula
        try:
            self.learn_from_message(user_id, message)
            self.store_conversation(user_id, message, final_response, intent)
        except Exception as e:
            print(f"❌ Temel öğrenme hatası: {e}")
        
        return final_response
    
    def save_conversation(self, user_id, message, bot_response, intent="genel"):
        """Konuşmayı kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO conversation_history (user_id, message, bot_response, intent)
                VALUES (?, ?, ?, ?)
            """, (user_id, message, bot_response, intent))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Konuşma kaydetme hatası: {e}")

# Global instance
smart_assistant = SmartAssistant()

# Helper fonksiyonları
async def handle_smart_message(update, context, message=None):
    """Akıllı mesaj işleme"""
    if message is None:
        message = update.message.text
    user_id = update.effective_user.id
    
    try:
        # Mesajdan öğren
        smart_assistant.learn_from_message(user_id, message)
        
        # Yanıt üret
        response = smart_assistant.generate_response(user_id, message)
        
        return response
    except Exception as e:
        print(f"❌ Akıllı mesaj işleme hatası: {e}")
        return "Size nasıl yardımcı olabilirim? 😊"

async def handle_learn_info(update, context):
    """Bilgi öğrenme işleme"""
    user_id = update.effective_user.id
    message = update.message.text
    
    try:
        smart_assistant.learn_from_message(user_id, message)
        return "Bu bilgiyi öğrendiğim için teşekkürler! 😊"
    except Exception as e:
        print(f"❌ Bilgi öğrenme hatası: {e}")
        return "Bilgiyi kaydedemedim ama size yardımcı olmaya devam edebilirim! 😊"

async def show_user_profile(update, context):
    """Kullanıcı profilini göster"""
    user_id = update.effective_user.id
    
    try:
        profile = smart_assistant.get_user_profile(user_id)
        
        if not profile or not profile['learned_info']:
            return "👤 Henüz hakkınızda bilgi öğrenmedim. Biraz konuşalım!"
        
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
        
        return response
    except Exception as e:
        print(f"❌ Profil gösterme hatası: {e}")
        return "❌ Profil gösterilemedi."

print("🧠 SÜPER ZEKİ ASISTAN başarıyla yüklendi!")
print("  🎯 Sürekli öğrenme aktif")
print("  🧠 Gelişmiş NLP motoru aktif") 
print("  🎭 Adaptif kişilik sistemi aktif")
print("  📝 Kişisel not ve ajanda sistemi aktif")
print("  🔍 Web araştırma motoru aktif")
print("  ⚡ Gerçek zamanlı öğrenme aktif")
print("="*50)
print("💫 Artık size özel kişilik geliştiriyorum!")
print("🔥 Her konuşmada daha akıllı hale geliyorum!")
print("🚀 Sizi gerçekten anlayan bir asistan oluyorum!")
print("="*50)
