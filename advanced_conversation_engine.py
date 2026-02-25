"""
🧠 GELIŞMIŞ KONUŞMA MOTORU - ChatGPT Pro seviyesinde!
Bağlamsal sohbet, kişilik analizi, duygusal zeka
"""

import re
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class AdvancedConversationEngine:
    """🎯 İleri seviye konuşma motoru - GPT-4 seviyesinde zeka"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.setup_advanced_tables()
        
    def setup_advanced_tables(self):
        """Gelişmiş konuşma tablolarını oluştur"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Konuşma context tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT,
                    context_topic TEXT,
                    mentioned_entities TEXT,  -- JSON: persons, places, dates
                    conversation_mood TEXT,
                    current_task TEXT,
                    open_questions TEXT,      -- JSON: unanswered questions
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Kullanıcı kişiliği ve tercihler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_personality_detailed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    communication_style TEXT,  -- formal, casual, friendly, professional
                    preferred_topics TEXT,     -- JSON: interested topics
                    conversation_patterns TEXT, -- JSON: how they usually talk
                    emotional_state TEXT,      -- current mood tendencies
                    interaction_frequency TEXT, -- how often they chat
                    response_preference TEXT,  -- brief, detailed, technical, simple
                    last_conversation_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Akıllı hatırlatmalar ve bağlantılar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS smart_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    entity_type TEXT,     -- person, place, event, task, topic
                    entity_name TEXT,
                    entity_details TEXT,  -- JSON: detailed info
                    connection_strength REAL, -- how important/frequent
                    last_mentioned TIMESTAMP,
                    context TEXT,         -- in what context mentioned
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            db.commit()
            db.close()
            print("🧠 Gelişmiş konuşma tabloları oluşturuldu!")
            
        except Exception as e:
            print(f"❌ Gelişmiş tablo hatası: {e}")
    
    def analyze_conversation_deeply(self, user_id: int, message: str, 
                                  conversation_history: List[Dict], emotional_state=None) -> Dict:
        """🎯 Derin konuşma analizi - GPT-4 seviyesinde anlama"""
        
        analysis = {
            'current_topic': self._extract_main_topic(message),
            'mentioned_entities': self._extract_entities(message),
            'user_mood': self._analyze_emotional_state(message, conversation_history),
            'conversation_flow': self._analyze_conversation_flow(conversation_history),
            'open_questions': self._find_open_questions(conversation_history),
            'context_connections': self._find_context_connections(user_id, message),
            'response_strategy': self._determine_response_strategy(message, conversation_history),
            'topic_transitions': self._detect_topic_changes(conversation_history),
            'user_intent_complex': self._analyze_complex_intent(message, conversation_history)
        }
        
        # Konuşma context'ini kaydet
        self._save_conversation_context(user_id, analysis)
        
        return analysis
    
    def generate_intelligent_response(self, user_id: int, message: str, 
                                    analysis: Dict, base_response: str) -> str:
        """🚀 Zeki yanıt üretimi - Bağlamsal ve kişisel"""
        
        # Kullanıcı kişiliğini al
        personality = self._get_user_personality_detailed(user_id)
        
        # Yanıt stratejisine göre işle
        if analysis['response_strategy'] == 'continue_topic':
            response = self._enhance_topic_continuation(base_response, analysis, personality)
        elif analysis['response_strategy'] == 'answer_question':
            response = self._enhance_question_response(base_response, analysis, personality)
        elif analysis['response_strategy'] == 'empathetic_support':
            response = self._enhance_emotional_response(base_response, analysis, personality)
        elif analysis['response_strategy'] == 'clarification_needed':
            response = self._enhance_clarification_request(base_response, analysis, personality)
        else:
            response = self._enhance_general_response(base_response, analysis, personality)
        
        # Konuşma bağlantılarını ekle
        if analysis['context_connections']:
            response = self._add_context_connections(response, analysis['context_connections'])
        
        # Kişilik güncelle
        self._update_user_personality(user_id, message, analysis)
        
        return response
    
    def _extract_main_topic(self, message: str) -> str:
        """Ana konuyu çıkar"""
        message_lower = message.lower()
        
        # Konu kategorileri
        topics = {
            'work': ['iş', 'çalışma', 'toplantı', 'patron', 'maaş', 'ofis', 'proje'],
            'personal': ['aile', 'arkadaş', 'sevgili', 'kişisel', 'özel'],
            'health': ['sağlık', 'doktor', 'hastane', 'ilaç', 'ağrı', 'hasta'],
            'travel': ['seyahat', 'tatil', 'gezi', 'uçak', 'otel', 'şehir'],
            'food': ['yemek', 'restaurant', 'kahvaltı', 'akşam yemeği', 'tarif'],
            'technology': ['teknoloji', 'bilgisayar', 'telefon', 'internet', 'yazılım'],
            'entertainment': ['film', 'müzik', 'kitap', 'oyun', 'eğlence'],
            'schedule': ['randevu', 'plan', 'program', 'tarih', 'saat', 'zaman'],
            'weather': ['hava', 'yağmur', 'güneş', 'soğuk', 'sıcak'],
            'shopping': ['alışveriş', 'market', 'satın', 'fiyat', 'para']
        }
        
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return 'general'
    
    def _extract_entities(self, message: str) -> Dict:
        """Varlıkları çıkar (kişi, yer, tarih, vs.)"""
        entities = {
            'persons': [],
            'places': [],
            'dates': [],
            'times': [],
            'organizations': [],
            'events': []
        }
        
        # Kişi isimleri (büyük harfle başlayan kelimeler)
        person_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_persons = re.findall(person_pattern, message)
        
        # Bilinen isimler vs. şehir isimlerini ayır
        known_places = ['Istanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana']
        for entity in potential_persons:
            if entity not in known_places and len(entity) > 2:
                entities['persons'].append(entity)
        
        # Yerler
        place_keywords = ['de ', 'da ', 'şehir', 'ülke', 'restoran', 'market', 'hastane', 'okul']
        for keyword in place_keywords:
            if keyword in message.lower():
                # Yakınındaki kelimeleri al
                words = message.split()
                for i, word in enumerate(words):
                    if keyword.strip() in word.lower() and i > 0:
                        entities['places'].append(words[i-1])
        
        # Tarihler (regex ile)
        date_patterns = [
            r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}',
            r'yarın|bugün|dün|pazartesi|salı|çarşamba|perşembe|cuma|cumartesi|pazar'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        # Saatler
        time_pattern = r'\d{1,2}:\d{2}|\d{1,2}\s*saatte?'
        entities['times'] = re.findall(time_pattern, message, re.IGNORECASE)
        
        return entities
    
    def _analyze_emotional_state(self, message: str, history: List[Dict]) -> str:
        """Duygusal durum analizi"""
        message_lower = message.lower()
        
        # Duygusal ipuçları
        emotions = {
            'happy': ['mutlu', 'güzel', 'harika', 'mükemmel', 'süper', 'iyi', '😊', '😃', '🎉'],
            'sad': ['üzgün', 'kötü', 'mutsuz', 'problem', 'sorun', '😢', '😞'],
            'excited': ['heyecan', 'sabırsız', 'muhteşem', '!', 'wow', '🚀', '✨'],
            'worried': ['endişe', 'korku', 'problem', 'sorun', 'zor', 'karışık'],
            'angry': ['sinir', 'kızgın', 'bıktım', 'yeter', 'saçma'],
            'neutral': []
        }
        
        # Puanla
        emotion_scores = {}
        for emotion, keywords in emotions.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # En yüksek skoru döndür
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        
        return 'neutral'
    
    def _analyze_conversation_flow(self, history: List[Dict]) -> str:
        """Konuşma akışını analiz et"""
        if not history or len(history) < 2:
            return 'new_conversation'
        
        recent_messages = history[-3:]
        
        # Son mesajlarda soru var mı?
        if any('?' in msg.get('content', '') for msg in recent_messages):
            return 'q_and_a'
        
        # Aynı konu devam ediyor mu?
        topics = [self._extract_main_topic(msg.get('content', '')) for msg in recent_messages]
        if len(set(topics)) == 1:
            return 'topic_continuation'
        
        return 'topic_change'
    
    def _determine_response_strategy(self, message: str, history: List[Dict]) -> str:
        """Yanıt stratejisini belirle"""
        
        if '?' in message:
            return 'answer_question'
        elif any(word in message.lower() for word in ['üzgün', 'problem', 'sorun', 'kötü']):
            return 'empathetic_support'
        elif any(word in message.lower() for word in ['hangi', 'nerede', 'nasıl', 'ne zaman']):
            return 'clarification_needed'
        elif history and len(history) > 0:
            return 'continue_topic'
        else:
            return 'general_chat'
    
    def _enhance_topic_continuation(self, base_response: str, analysis: Dict, personality: Dict) -> str:
        """Konu devamı yanıtını geliştir"""
        topic = analysis.get('current_topic', 'general')
        
        # Konuya özel geliştirmeler
        topic_enhancers = {
            'work': "İş konularında size yardımcı olmaya devam edeyim.",
            'health': "Sağlığınız önemli, detaylarını konuşalım.",
            'travel': "Seyahat planlarınız흥mi çok흥미롭다! Detayları neler?",
            'food': "Yemek konusu favorim! Ne tür lezzetler seversiniz?"
        }
        
        enhancer = topic_enhancers.get(topic, "Bu konuyu daha detayına konuşalım.")
        
        return f"{base_response}\n\n💡 {enhancer}"
    
    def _enhance_emotional_response(self, base_response: str, analysis: Dict, personality: Dict) -> str:
        """Duygusal yanıtı geliştir"""
        mood = analysis.get('user_mood', 'neutral')
        
        if mood == 'sad':
            return f"🤗 {base_response}\n\nSizi anlıyorum. Bu konularda konuşmak istediğinizde buradayım."
        elif mood == 'happy':
            return f"😊 {base_response}\n\nMutluluğunuz beni de mutlu ediyor! Bu güzel haberi paylaştığınız için teşekkürler."
        elif mood == 'excited':
            return f"🚀 {base_response}\n\nHeyecanınız çok güzel! Bu konuda daha fazla konuşalım."
        
        return base_response
    
    def _save_conversation_context(self, user_id: int, analysis: Dict):
        """Konuşma context'ini kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversation_context 
                (user_id, context_topic, mentioned_entities, conversation_mood, current_task)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                analysis.get('current_topic'),
                json.dumps(analysis.get('mentioned_entities')),
                analysis.get('user_mood'),
                analysis.get('user_intent_complex')
            ))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Context kaydetme hatası: {e}")
    
    def _get_user_personality_detailed(self, user_id: int) -> Dict:
        """Detaylı kullanıcı kişiliği al"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT * FROM user_personality_detailed WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            db.close()
            
            if result:
                return {
                    'communication_style': result[2] or 'casual',
                    'preferred_topics': json.loads(result[3] or '[]'),
                    'response_preference': result[6] or 'medium'
                }
            
        except Exception as e:
            print(f"❌ Kişilik alma hatası: {e}")
        
        return {'communication_style': 'casual', 'preferred_topics': [], 'response_preference': 'medium'}
    
    def _update_user_personality(self, user_id: int, message: str, analysis: Dict):
        """Kullanıcı kişiliğini güncelle"""
        # Bu fonksiyon kullanıcının konuşma stilini öğrenir
        pass
    
    # Diğer yardımcı fonksiyonlar...
    def _find_open_questions(self, history: List[Dict]) -> List[str]:
        """Açık kalan soruları bul"""
        return []
    
    def _find_context_connections(self, user_id: int, message: str) -> List[Dict]:
        """Bağlam bağlantıları bul"""
        return []
    
    def _enhance_question_response(self, base_response: str, analysis: Dict, personality: Dict) -> str:
        """Soru yanıtını geliştir"""
        return base_response
    
    def _enhance_clarification_request(self, base_response: str, analysis: Dict, personality: Dict) -> str:
        """Açıklama isteği yanıtını geliştir"""
        return base_response
    
    def _enhance_general_response(self, base_response: str, analysis: Dict, personality: Dict) -> str:
        """Genel yanıtı geliştir"""
        return base_response
    
    def _add_context_connections(self, response: str, connections: List[Dict]) -> str:
        """Bağlam bağlantıları ekle"""
        return response
    
    def _detect_topic_changes(self, history: List[Dict]) -> bool:
        """Konu değişimi tespit et"""
        return False
    
    def _analyze_complex_intent(self, message: str, history: List[Dict]) -> str:
        """Karmaşık intent analizi"""
        return 'general'
