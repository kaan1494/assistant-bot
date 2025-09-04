"""
🧠 SÜPER HAFIZA VE ÖĞRENME SİSTEMİ - ChatGPT Pro seviyesinde!
Her konuşmayı hatırlar, öğrenir ve kişiselleşir
"""

import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re

class SuperMemoryLearningSystem:
    """🧠 Süper Hafıza ve Öğrenme Sistemi"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.setup_memory_tables()
        self.knowledge_categories = self._load_knowledge_categories()
        
    def setup_memory_tables(self):
        """Hafıza tablolarını oluştur"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Kullanıcı hafızası - kişisel bilgiler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    memory_type TEXT, -- personal_info, preferences, habits, relationships
                    memory_key TEXT,  -- name, job, hobby, friend_name, etc.
                    memory_value TEXT,
                    confidence_score REAL DEFAULT 1.0,
                    first_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mention_count INTEGER DEFAULT 1,
                    context TEXT,     -- in what context mentioned
                    UNIQUE(user_id, memory_type, memory_key)
                )
            """)
            
            # Konuşma konuları ve ilgi alanları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_interests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    topic TEXT,
                    interest_level REAL DEFAULT 1.0, -- 0-10 scale
                    last_discussed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    discussion_count INTEGER DEFAULT 1,
                    favorite_subtopics TEXT, -- JSON array
                    learning_progress TEXT,  -- JSON: what they learned about this topic
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Kullanıcının öğrenmek istediği şeyler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    goal_topic TEXT,
                    goal_description TEXT,
                    target_level TEXT, -- beginner, intermediate, advanced
                    current_progress REAL DEFAULT 0.0, -- 0-100%
                    learning_style TEXT, -- visual, auditory, hands-on, reading
                    preferred_pace TEXT, -- slow, normal, fast
                    status TEXT DEFAULT 'active', -- active, completed, paused, cancelled
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    target_date TIMESTAMP
                )
            """)
            
            # Başarılar ve kilometre taşları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    achievement_type TEXT, -- conversation_count, topic_mastery, goal_completion
                    achievement_name TEXT,
                    achievement_description TEXT,
                    earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    celebration_sent BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Kullanıcının soruları ve merakları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_curiosities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    question TEXT,
                    topic_category TEXT,
                    answered BOOLEAN DEFAULT FALSE,
                    answer_quality TEXT, -- satisfactory, needs_more, complex
                    follow_up_needed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    answered_at TIMESTAMP
                )
            """)
            
            db.commit()
            db.close()
            print("🧠 Süper hafıza tabloları oluşturuldu!")
            
        except Exception as e:
            print(f"❌ Hafıza tablo hatası: {e}")
    
    def extract_and_store_memories(self, user_id: int, message: str, 
                                 conversation_context: Dict = None) -> Dict:
        """🎯 Mesajdan anıları çıkar ve sakla"""
        
        memories = {
            'personal_info': self._extract_personal_info(message),
            'preferences': self._extract_preferences(message),
            'relationships': self._extract_relationships(message),
            'habits': self._extract_habits(message),
            'goals': self._extract_goals(message),
            'interests': self._extract_interests(message),
            'questions': self._extract_questions(message)
        }
        
        # Her kategoriyi veritabanına kaydet
        for memory_type, extracted_memories in memories.items():
            for memory in extracted_memories:
                self._store_memory(user_id, memory_type, memory, message)
        
        # İlgi alanlarını güncelle
        self._update_interests(user_id, message)
        
        # Öğrenme hedeflerini kontrol et
        self._check_learning_progress(user_id, message)
        
        return memories
    
    def _extract_personal_info(self, message: str) -> List[Dict]:
        """👤 Kişisel bilgileri çıkar"""
        personal_info = []
        message_lower = message.lower()
        
        # İsim çıkarma
        name_patterns = [
            r'adım\s+([A-Za-zÇĞıÖŞÜçğıöşü]+)',
            r'benim adım\s+([A-Za-zÇĞıÖŞÜçğıöşü]+)',
            r'ben\s+([A-Za-zÇĞıÖŞÜçğıöşü]+)',
            r'ismim\s+([A-Za-zÇĞıÖŞÜçğıöşü]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).title()
                personal_info.append({
                    'key': 'name',
                    'value': name,
                    'confidence': 0.9
                })
        
        # Yaş çıkarma
        age_patterns = [
            r'(\d+)\s*yaşında',
            r'yaşım\s*(\d+)',
            r'(\d+)\s*yaşım'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, message_lower)
            if match:
                age = match.group(1)
                personal_info.append({
                    'key': 'age',
                    'value': age,
                    'confidence': 0.95
                })
        
        # Meslek çıkarma
        job_keywords = [
            'işim', 'mesleğim', 'çalışıyorum', 'iş', 'şirket', 'firma', 'ofis',
            'doktor', 'öğretmen', 'mühendis', 'avukat', 'hemşire', 'yazılımcı'
        ]
        
        for keyword in job_keywords:
            if keyword in message_lower:
                # Yakınındaki kelimeleri al
                words = message.split()
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        # Öncesi ve sonrası 2-3 kelimeyi kontrol et
                        context_words = words[max(0, i-2):i+3]
                        job_info = ' '.join(context_words)
                        personal_info.append({
                            'key': 'job',
                            'value': job_info,
                            'confidence': 0.7
                        })
                        break
        
        # Şehir/Konum çıkarma
        location_patterns = [
            r'([A-Za-zÇĞıÖŞÜçğıöşü]+)\'?(?:da|de|ta|te)\s+yaşıyorum',
            r'yaşadığım\s+yer\s+([A-Za-zÇĞıÖŞÜçğıöşü]+)',
            r'([A-Za-zÇĞıÖŞÜçğıöşü]+)\'?(?:dan|den)\s+geliyorum'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                location = match.group(1).title()
                personal_info.append({
                    'key': 'location',
                    'value': location,
                    'confidence': 0.8
                })
        
        return personal_info
    
    def _extract_preferences(self, message: str) -> List[Dict]:
        """💝 Tercihleri çıkar"""
        preferences = []
        message_lower = message.lower()
        
        # Favori şeyler
        favorite_patterns = [
            r'favorim\s+(.+)',
            r'en\s+sevdiğim\s+(.+)',
            r'çok\s+severim\s+(.+)',
            r'bayılırım\s+(.+)'
        ]
        
        for pattern in favorite_patterns:
            match = re.search(pattern, message_lower)
            if match:
                favorite_item = match.group(1)
                preferences.append({
                    'key': 'favorite',
                    'value': favorite_item,
                    'confidence': 0.8
                })
        
        # Sevmediği şeyler
        dislike_patterns = [
            r'sevmiyorum\s+(.+)',
            r'hiç\s+sevmem\s+(.+)',
            r'nefret\s+ediyorum\s+(.+)'
        ]
        
        for pattern in dislike_patterns:
            match = re.search(pattern, message_lower)
            if match:
                dislike_item = match.group(1)
                preferences.append({
                    'key': 'dislike',
                    'value': dislike_item,
                    'confidence': 0.8
                })
        
        return preferences
    
    def _extract_relationships(self, message: str) -> List[Dict]:
        """👨‍👩‍👧‍👦 İlişkileri çıkar"""
        relationships = []
        message_lower = message.lower()
        
        # Aile ve arkadaş ilişkileri
        relationship_patterns = [
            r'(?:benim\s+)?(?:annem|babam|kardeşim|eşim|sevgilim|arkadaşım)\s+([A-Za-zÇĞıÖŞÜçğıöşü]+)',
            r'([A-Za-zÇĞıÖŞÜçğıöşü]+)\s+(?:isimli|adında)\s+(?:arkadaşım|dostum|kardeşim)',
            r'([A-Za-zÇĞıÖŞÜçğıöşü]+)\s+ile\s+(?:evliyim|birlikte yaşıyorum|arkadaşım)'
        ]
        
        relationship_types = {
            'anne': 'mother', 'annem': 'mother',
            'baba': 'father', 'babam': 'father',
            'kardeş': 'sibling', 'kardeşim': 'sibling',
            'eş': 'spouse', 'eşim': 'spouse',
            'sevgili': 'partner', 'sevgilim': 'partner',
            'arkadaş': 'friend', 'arkadaşım': 'friend'
        }
        
        for word, rel_type in relationship_types.items():
            if word in message_lower:
                # İsim çıkarmaya çalış
                words = message.split()
                for i, w in enumerate(words):
                    if word in w.lower() and i < len(words) - 1:
                        potential_name = words[i + 1]
                        if potential_name.istitle():
                            relationships.append({
                                'key': rel_type,
                                'value': potential_name,
                                'confidence': 0.7
                            })
        
        return relationships
    
    def _extract_habits(self, message: str) -> List[Dict]:
        """🔄 Alışkanlıkları çıkar"""
        habits = []
        message_lower = message.lower()
        
        # Rutin aktiviteler
        habit_patterns = [
            r'her\s+(?:gün|sabah|akşam)\s+(.+)',
            r'genellikle\s+(.+)',
            r'hep\s+(.+)',
            r'sürekli\s+(.+)',
            r'alışkanlığım\s+(.+)'
        ]
        
        for pattern in habit_patterns:
            match = re.search(pattern, message_lower)
            if match:
                habit = match.group(1)
                habits.append({
                    'key': 'routine',
                    'value': habit,
                    'confidence': 0.6
                })
        
        return habits
    
    def _extract_goals(self, message: str) -> List[Dict]:
        """🎯 Hedefleri çıkar"""
        goals = []
        message_lower = message.lower()
        
        # Hedef ifadeleri
        goal_patterns = [
            r'hedefim\s+(.+)',
            r'istiyorum\s+(.+)',
            r'yapmak\s+istiyorum\s+(.+)',
            r'öğrenmek\s+istiyorum\s+(.+)',
            r'planım\s+(.+)'
        ]
        
        for pattern in goal_patterns:
            match = re.search(pattern, message_lower)
            if match:
                goal = match.group(1)
                goals.append({
                    'key': 'goal',
                    'value': goal,
                    'confidence': 0.7
                })
        
        return goals
    
    def _extract_interests(self, message: str) -> List[Dict]:
        """🌟 İlgi alanlarını çıkar"""
        interests = []
        message_lower = message.lower()
        
        # İlgi konuları
        interest_keywords = {
            'spor': ['futbol', 'basketbol', 'tenis', 'yüzme', 'koşu', 'fitness'],
            'müzik': ['şarkı', 'müzik', 'enstrüman', 'konser', 'albüm'],
            'teknoloji': ['bilgisayar', 'yazılım', 'programlama', 'yapay zeka', 'robot'],
            'sanat': ['resim', 'heykel', 'sinema', 'tiyatro', 'edebiyat'],
            'bilim': ['fizik', 'kimya', 'biyoloji', 'matematik', 'astronomi'],
            'seyahat': ['gezi', 'tatil', 'ülke', 'şehir', 'kültür'],
            'yemek': ['yemek', 'tarif', 'restaurant', 'mutfak', 'lezzet']
        }
        
        for category, keywords in interest_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                interests.append({
                    'key': 'interest_category',
                    'value': category,
                    'confidence': 0.6
                })
        
        return interests
    
    def _extract_questions(self, message: str) -> List[Dict]:
        """❓ Soruları çıkar"""
        questions = []
        
        if '?' in message:
            questions.append({
                'key': 'question',
                'value': message.strip(),
                'confidence': 1.0
            })
        
        # Merak ifadeleri
        curiosity_patterns = [
            r'merak\s+ediyorum\s+(.+)',
            r'bilmek\s+istiyorum\s+(.+)',
            r'öğrenmek\s+istiyorum\s+(.+)'
        ]
        
        for pattern in curiosity_patterns:
            match = re.search(pattern, message.lower())
            if match:
                curiosity = match.group(1)
                questions.append({
                    'key': 'curiosity',
                    'value': curiosity,
                    'confidence': 0.8
                })
        
        return questions
    
    def _store_memory(self, user_id: int, memory_type: str, memory: Dict, context: str):
        """💾 Hafızayı kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Var olan hafızayı kontrol et
            cursor.execute("""
                SELECT id, mention_count, confidence_score FROM user_memory 
                WHERE user_id = ? AND memory_type = ? AND memory_key = ?
            """, (user_id, memory_type, memory['key']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Güncelle
                new_count = existing[1] + 1
                new_confidence = min(1.0, existing[2] + 0.1)  # Güven arttır
                
                cursor.execute("""
                    UPDATE user_memory 
                    SET memory_value = ?, mention_count = ?, confidence_score = ?,
                        last_updated = CURRENT_TIMESTAMP, context = ?
                    WHERE id = ?
                """, (memory['value'], new_count, new_confidence, context, existing[0]))
            else:
                # Yeni kayıt
                cursor.execute("""
                    INSERT INTO user_memory 
                    (user_id, memory_type, memory_key, memory_value, confidence_score, context)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, memory_type, memory['key'], memory['value'], 
                      memory['confidence'], context))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Hafıza kaydetme hatası: {e}")
    
    def get_user_memories(self, user_id: int) -> Dict:
        """🧠 Kullanıcı hafızasını getir"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT memory_type, memory_key, memory_value, confidence_score, mention_count
                FROM user_memory 
                WHERE user_id = ? AND confidence_score > 0.5
                ORDER BY confidence_score DESC, mention_count DESC
            """, (user_id,))
            
            memories = cursor.fetchall()
            db.close()
            
            # Kategorilere ayır
            organized_memories = {}
            for memory in memories:
                memory_type = memory[0]
                if memory_type not in organized_memories:
                    organized_memories[memory_type] = []
                
                organized_memories[memory_type].append({
                    'key': memory[1],
                    'value': memory[2],
                    'confidence': memory[3],
                    'mentions': memory[4]
                })
            
            return organized_memories
            
        except Exception as e:
            print(f"❌ Hafıza getirme hatası: {e}")
            return {}
    
    def generate_personalized_context(self, user_id: int) -> str:
        """👤 Kişiselleştirilmiş bağlam oluştur"""
        memories = self.get_user_memories(user_id)
        
        if not memories:
            return ""
        
        context_parts = []
        
        # Kişisel bilgiler
        if 'personal_info' in memories:
            personal = memories['personal_info']
            name = next((m['value'] for m in personal if m['key'] == 'name'), None)
            if name:
                context_parts.append(f"👤 Kullanıcının adı: {name}")
            
            job = next((m['value'] for m in personal if m['key'] == 'job'), None)
            if job:
                context_parts.append(f"💼 Meslek/İş: {job}")
        
        # Tercihler
        if 'preferences' in memories:
            prefs = memories['preferences']
            favorites = [m['value'] for m in prefs if m['key'] == 'favorite']
            if favorites:
                context_parts.append(f"💝 Sevdiği şeyler: {', '.join(favorites[:3])}")
        
        # İlişkiler
        if 'relationships' in memories:
            rels = memories['relationships']
            family = [f"{m['key']}: {m['value']}" for m in rels]
            if family:
                context_parts.append(f"👨‍👩‍👧‍👦 Aile/Arkadaşlar: {', '.join(family[:3])}")
        
        return "\n".join(context_parts)
    
    def _load_knowledge_categories(self) -> Dict:
        """📚 Bilgi kategorilerini yükle"""
        return {
            'general': ['genel kültür', 'güncel haberler', 'tarih', 'coğrafya'],
            'technology': ['programlama', 'yapay zeka', 'bilgisayar', 'internet'],
            'science': ['fizik', 'kimya', 'biyoloji', 'matematik', 'astronomi'],
            'health': ['sağlık', 'beslenme', 'egzersiz', 'hastalık', 'ilaç'],
            'art': ['müzik', 'resim', 'sinema', 'edebiyat', 'tiyatro'],
            'sports': ['futbol', 'basketbol', 'spor', 'fitness', 'atletizm'],
            'cooking': ['yemek', 'tarif', 'mutfak', 'beslenme', 'lezzet'],
            'travel': ['seyahat', 'ülke', 'şehir', 'kültür', 'tatil']
        }
    
    def _update_interests(self, user_id: int, message: str):
        """🌟 İlgi alanlarını güncelle"""
        # Bu fonksiyon konuşma analiz ederek ilgi seviyelerini günceller
        pass
    
    def _check_learning_progress(self, user_id: int, message: str):
        """📈 Öğrenme ilerlemesini kontrol et"""
        # Bu fonksiyon kullanıcının öğrenme hedeflerini takip eder
        pass
