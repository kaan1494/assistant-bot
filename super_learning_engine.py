"""
SÜPER ZEKİ ÖĞRENME MOTORU
Her konuşmada öğrenen, gelişen ve kullanıcıyı gerçekten anlayan yapay zeka
"""

import sqlite3
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math

class SuperLearningEngine:
    """Sürekli öğrenen süper zeka motoru"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.user_memories = {}  # Kullanıcı hafızası
        self.conversation_context = {}  # Konuşma bağlamı
        self.learning_patterns = {}  # Öğrenme kalıpları
        self.personality_models = {}  # Kişilik modelleri
        
        self.setup_super_database()
        print("🧠 SÜPER ZEKİ ÖĞRENME MOTORU aktif!")
    
    def setup_super_database(self):
        """Süper öğrenme için gelişmiş veritabanı"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Kullanıcı kişilik profili
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_personality (
                    user_id INTEGER,
                    trait_name TEXT,
                    trait_value REAL,
                    confidence REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    evidence_count INTEGER DEFAULT 1,
                    PRIMARY KEY (user_id, trait_name)
                )
            """)
            
            # Duygu analizi geçmişi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emotion_history (
                    user_id INTEGER,
                    message TEXT,
                    detected_emotion TEXT,
                    emotion_intensity REAL,
                    context_tags TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Konu uzmanları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_expertise (
                    user_id INTEGER,
                    topic TEXT,
                    expertise_level REAL,
                    interest_level REAL,
                    conversation_count INTEGER DEFAULT 1,
                    last_discussed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, topic)
                )
            """)
            
            # Konuşma kalıpları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_patterns (
                    user_id INTEGER,
                    pattern_type TEXT,
                    pattern_value TEXT,
                    frequency INTEGER DEFAULT 1,
                    effectiveness REAL DEFAULT 0.5,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Öğrenme başarıları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_achievements (
                    user_id INTEGER,
                    achievement_type TEXT,
                    description TEXT,
                    confidence_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            db.commit()
            db.close()
            print("✅ Süper öğrenme veritabanı kuruldu!")
            
        except Exception as e:
            print(f"❌ Süper veritabanı hatası: {e}")
    
    def analyze_super_deep(self, user_id, message):
        """Süper derin analiz - Her kelimeyi, duyguyu, niyeti analiz et"""
        analysis = {
            'emotional_state': self.detect_emotions(message),
            'personality_traits': self.extract_personality_traits(message),
            'interests': self.detect_interests(message),
            'communication_style': self.analyze_communication_style(message),
            'knowledge_level': self.assess_knowledge_level(message),
            'context_clues': self.extract_context_clues(message),
            'hidden_meanings': self.detect_hidden_meanings(message),
            'future_needs': self.predict_future_needs(message)
        }
        
        # Analizi kaydet ve öğren
        self.store_deep_analysis(user_id, message, analysis)
        
        return analysis
    
    def detect_emotions(self, message):
        """Gelişmiş duygu analizi"""
        emotions = {}
        message_lower = message.lower()
        
        # Pozitif duygular
        positive_indicators = {
            'happiness': ['mutlu', 'sevinç', 'harika', 'güzel', 'süper', 'mükemmel', 'bayılıyorum', 'çok iyi'],
            'excitement': ['heyecan', 'sabırsız', 'merakla', 'çok istiyorum', 'harika olacak'],
            'gratitude': ['teşekkür', 'sağol', 'minnettarım', 'yardımın için'],
            'love': ['seviyorum', 'aşık', 'bayılıyorum', 'çok beğeniyorum']
        }
        
        # Negatif duygular
        negative_indicators = {
            'frustration': ['sinir', 'bıktım', 'yoruldum', 'usandım', 'berbat', 'rezalet'],
            'sadness': ['üzgün', 'kötü', 'depresif', 'mutsuz', 'karamsar'],
            'anger': ['kızgın', 'öfke', 'sinirli', 'deliriyorum', 'çileden çıktım'],
            'worry': ['endişe', 'kaygı', 'korku', 'tedirgin', 'gergin']
        }
        
        # Duygu skorları hesapla
        for emotion, indicators in {**positive_indicators, **negative_indicators}.items():
            score = sum(1 for indicator in indicators if indicator in message_lower)
            if score > 0:
                emotions[emotion] = min(1.0, score / 3)  # Normalize et
        
        return emotions
    
    def extract_personality_traits(self, message):
        """Kişilik özelliklerini çıkar"""
        traits = {}
        message_lower = message.lower()
        
        # Dışadönüklük
        extroversion_indicators = ['sosyal', 'parti', 'insanlar', 'buluşma', 'konuşmak', 'arkadaş']
        if any(word in message_lower for word in extroversion_indicators):
            traits['extroversion'] = 0.7
        
        # Açıklık
        openness_indicators = ['yeni', 'farklı', 'deneyim', 'öğrenmek', 'keşfetmek', 'merak']
        if any(word in message_lower for word in openness_indicators):
            traits['openness'] = 0.8
        
        # Sorumluluk
        conscientiousness_indicators = ['plan', 'organize', 'düzen', 'zamanında', 'sorumlu']
        if any(word in message_lower for word in conscientiousness_indicators):
            traits['conscientiousness'] = 0.6
        
        # Uyumluluk
        agreeableness_indicators = ['yardım', 'anlayış', 'empati', 'düşünceli', 'nazik']
        if any(word in message_lower for word in agreeableness_indicators):
            traits['agreeableness'] = 0.7
        
        # Nevrotizm
        neuroticism_indicators = ['stres', 'endişe', 'kaygı', 'gergin', 'sinirli']
        if any(word in message_lower for word in neuroticism_indicators):
            traits['neuroticism'] = 0.6
        
        return traits
    
    def detect_interests(self, message):
        """İlgi alanlarını gelişmiş şekilde tespit et"""
        interests = {}
        message_lower = message.lower()
        
        # Teknoloji
        tech_words = ['python', 'kod', 'program', 'yazılım', 'bilgisayar', 'ai', 'yapay zeka', 'robot']
        tech_score = sum(1 for word in tech_words if word in message_lower)
        if tech_score > 0:
            interests['technology'] = min(1.0, tech_score / 3)
        
        # Spor
        sport_words = ['futbol', 'basketbol', 'tenis', 'yüzme', 'koşu', 'fitness', 'gym']
        sport_score = sum(1 for word in sport_words if word in message_lower)
        if sport_score > 0:
            interests['sports'] = min(1.0, sport_score / 3)
        
        # Sanat
        art_words = ['müzik', 'resim', 'film', 'kitap', 'şarkı', 'dans', 'tiyatro']
        art_score = sum(1 for word in art_words if word in message_lower)
        if art_score > 0:
            interests['arts'] = min(1.0, art_score / 3)
        
        # Bilim
        science_words = ['fizik', 'kimya', 'biyoloji', 'matematik', 'astronomi', 'deneyim']
        science_score = sum(1 for word in science_words if word in message_lower)
        if science_score > 0:
            interests['science'] = min(1.0, science_score / 3)
        
        return interests
    
    def analyze_communication_style(self, message):
        """İletişim tarzını analiz et"""
        style = {}
        
        # Mesaj uzunluğu
        words = message.split()
        if len(words) > 20:
            style['verbosity'] = 'high'
        elif len(words) < 5:
            style['verbosity'] = 'low'
        else:
            style['verbosity'] = 'medium'
        
        # Emoji kullanımı
        emoji_count = len(re.findall(r'[😀-🙏]|:\)|:\(|:D|;-\)', message))
        if emoji_count > 0:
            style['emoji_usage'] = 'frequent'
        else:
            style['emoji_usage'] = 'rare'
        
        # Soru sorma eğilimi
        question_count = message.count('?')
        if question_count > 2:
            style['curiosity'] = 'high'
        elif question_count > 0:
            style['curiosity'] = 'medium'
        else:
            style['curiosity'] = 'low'
        
        # Kibar dil kullanımı
        polite_words = ['lütfen', 'teşekkür', 'rica', 'özür', 'pardon']
        if any(word in message.lower() for word in polite_words):
            style['politeness'] = 'high'
        else:
            style['politeness'] = 'medium'
        
        return style
    
    def assess_knowledge_level(self, message):
        """Bilgi seviyesini değerlendir"""
        knowledge = {}
        message_lower = message.lower()
        
        # Teknik terimler
        technical_terms = ['algoritma', 'veri', 'fonksiyon', 'sistem', 'analiz', 'optimizasyon']
        tech_count = sum(1 for term in technical_terms if term in message_lower)
        knowledge['technical'] = min(1.0, tech_count / 3)
        
        # Kompleks cümleler
        complex_indicators = [';', 'ancak', 'buna rağmen', 'diğer taraftan', 'ayrıca']
        complex_count = sum(1 for indicator in complex_indicators if indicator in message_lower)
        knowledge['complexity'] = min(1.0, complex_count / 2)
        
        return knowledge
    
    def extract_context_clues(self, message):
        """Bağlam ipuçlarını çıkar"""
        context = {}
        message_lower = message.lower()
        
        # Zaman referansları
        time_refs = ['dün', 'bugün', 'yarın', 'geçen hafta', 'gelecek ay', 'önce', 'sonra']
        for ref in time_refs:
            if ref in message_lower:
                context['time_reference'] = ref
                break
        
        # Lokasyon referansları
        location_refs = ['evde', 'işte', 'okulda', 'dışarıda', 'burada', 'orada']
        for ref in location_refs:
            if ref in message_lower:
                context['location'] = ref
                break
        
        return context
    
    def detect_hidden_meanings(self, message):
        """Gizli anlamları tespit et"""
        hidden = {}
        message_lower = message.lower()
        
        # İroni/sarkazm
        irony_indicators = ['tabii canım', 'çok güzel', 'harika ya', 'süper be']
        if any(indicator in message_lower for indicator in irony_indicators):
            hidden['irony_potential'] = 0.7
        
        # Pasif agresiflik
        passive_aggressive = ['sorun değil', 'önemli değil', 'nasıl istersen', 'sen bilirsin']
        if any(phrase in message_lower for phrase in passive_aggressive):
            hidden['passive_aggressive'] = 0.6
        
        return hidden
    
    def predict_future_needs(self, message):
        """Gelecekteki ihtiyaçları tahmin et"""
        predictions = {}
        message_lower = message.lower()
        
        # Öğrenme ihtiyacı
        if any(word in message_lower for word in ['bilmiyorum', 'öğrenmek istiyorum', 'nasıl']):
            predictions['learning_need'] = 0.8
        
        # Planlama ihtiyacı
        if any(word in message_lower for word in ['plan', 'organize', 'düzenle']):
            predictions['planning_need'] = 0.7
        
        # Sosyal destek ihtiyacı
        if any(word in message_lower for word in ['yalnız', 'sıkıldım', 'birisiyle konuşmak']):
            predictions['social_support_need'] = 0.9
        
        return predictions
    
    def store_deep_analysis(self, user_id, message, analysis):
        """Derin analizi veritabanına kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Duyguları kaydet
            for emotion, intensity in analysis['emotional_state'].items():
                cursor.execute("""
                    INSERT INTO emotion_history (user_id, message, detected_emotion, emotion_intensity)
                    VALUES (?, ?, ?, ?)
                """, (user_id, message[:200], emotion, intensity))
            
            # Kişilik özelliklerini güncelle
            for trait, value in analysis['personality_traits'].items():
                cursor.execute("""
                    INSERT OR REPLACE INTO user_personality 
                    (user_id, trait_name, trait_value, confidence, evidence_count)
                    VALUES (?, ?, ?, ?, 
                           COALESCE((SELECT evidence_count FROM user_personality 
                                   WHERE user_id=? AND trait_name=?), 0) + 1)
                """, (user_id, trait, value, 0.8, user_id, trait))
            
            # İlgi alanlarını güncelle
            for topic, level in analysis['interests'].items():
                cursor.execute("""
                    INSERT OR REPLACE INTO topic_expertise 
                    (user_id, topic, interest_level, conversation_count)
                    VALUES (?, ?, ?, 
                           COALESCE((SELECT conversation_count FROM topic_expertise 
                                   WHERE user_id=? AND topic=?), 0) + 1)
                """, (user_id, topic, level, user_id, topic))
            
            # Konuşma kalıplarını kaydet
            for style_type, style_value in analysis['communication_style'].items():
                cursor.execute("""
                    INSERT INTO conversation_patterns (user_id, pattern_type, pattern_value)
                    VALUES (?, ?, ?)
                """, (user_id, f"communication_{style_type}", str(style_value)))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Analiz kaydetme hatası: {e}")
    
    def generate_adaptive_response(self, user_id, message, base_response):
        """Kullanıcıya uyarlanmış yanıt üret"""
        try:
            # Kullanıcı profilini al
            user_profile = self.get_user_super_profile(user_id)
            
            # Yanıtı kişiselleştir
            personalized_response = self.personalize_response(
                base_response, user_profile, message
            )
            
            return personalized_response
            
        except Exception as e:
            print(f"❌ Adaptif yanıt hatası: {e}")
            return base_response
    
    def get_user_super_profile(self, user_id):
        """Kullanıcının süper profilini al"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            profile = {
                'personality': {},
                'interests': {},
                'communication_style': {},
                'emotional_patterns': {},
                'learning_achievements': []
            }
            
            # Kişilik özellikleri
            cursor.execute("""
                SELECT trait_name, trait_value, confidence, evidence_count
                FROM user_personality WHERE user_id = ?
            """, (user_id,))
            for row in cursor.fetchall():
                profile['personality'][row[0]] = {
                    'value': row[1],
                    'confidence': row[2],
                    'evidence': row[3]
                }
            
            # İlgi alanları
            cursor.execute("""
                SELECT topic, interest_level, conversation_count
                FROM topic_expertise WHERE user_id = ?
            """, (user_id,))
            for row in cursor.fetchall():
                profile['interests'][row[0]] = {
                    'level': row[1],
                    'conversations': row[2]
                }
            
            # Son duygular
            cursor.execute("""
                SELECT detected_emotion, emotion_intensity, timestamp
                FROM emotion_history WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT 5
            """, (user_id,))
            profile['emotional_patterns'] = cursor.fetchall()
            
            db.close()
            return profile
            
        except Exception as e:
            print(f"❌ Profil alma hatası: {e}")
            return {}
    
    def personalize_response(self, response, profile, original_message):
        """Yanıtı kişiselleştir"""
        try:
            personalized = response
            
            # Kişilik özelliklerine göre ton ayarla
            if profile.get('personality', {}).get('extroversion', {}).get('value', 0) > 0.7:
                # Daha enerjik yanıt
                personalized = personalized.replace(".", "! 🎉")
                personalized += "\n\nBu konuda daha fazla konuşalım! 😊"
            
            # İlgi alanlarına göre ek bilgi ekle
            interests = profile.get('interests', {})
            if 'technology' in interests and interests['technology']['level'] > 0.5:
                if any(word in original_message.lower() for word in ['kod', 'program', 'teknoloji']):
                    personalized += "\n\n🤖 Teknoloji konularında size daha fazla yardımcı olabilirim!"
            
            # Duygusal duruma göre yaklaşım
            recent_emotions = profile.get('emotional_patterns', [])
            if recent_emotions:
                last_emotion = recent_emotions[0]
                if 'sadness' in last_emotion[0] or 'worry' in last_emotion[0]:
                    personalized += "\n\n💙 Her zaman yanınızdayım, merak etmeyin!"
            
            return personalized
            
        except Exception as e:
            print(f"❌ Kişiselleştirme hatası: {e}")
            return response
    
    def continuous_learning_update(self, user_id, message, bot_response, user_feedback=None):
        """Sürekli öğrenme güncellemesi"""
        try:
            # Her konuşmadan öğren
            analysis = self.analyze_super_deep(user_id, message)
            
            # Başarı metriklerini güncelle
            self.update_learning_metrics(user_id, analysis)
            
            # Kişilik modelini güncelle
            self.update_personality_model(user_id, analysis)
            
            # Yanıt kalitesini değerlendir
            if user_feedback:
                self.update_response_quality(user_id, message, bot_response, user_feedback)
            
            print(f"🧠 Kullanıcı {user_id} için öğrenme güncellendi!")
            
        except Exception as e:
            print(f"❌ Sürekli öğrenme hatası: {e}")
    
    def update_learning_metrics(self, user_id, analysis):
        """Öğrenme metriklerini güncelle"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Yeni başarılar kaydet
            achievements = []
            
            if analysis['interests']:
                achievements.append(("interest_discovery", f"Yeni ilgi alanı tespit edildi: {list(analysis['interests'].keys())}", 0.8))
            
            if analysis['personality_traits']:
                achievements.append(("personality_insight", f"Kişilik özelliği güncellendi: {list(analysis['personality_traits'].keys())}", 0.7))
            
            if analysis['emotional_state']:
                achievements.append(("emotion_recognition", f"Duygu tanındı: {list(analysis['emotional_state'].keys())}", 0.9))
            
            for achievement_type, description, confidence in achievements:
                cursor.execute("""
                    INSERT INTO learning_achievements 
                    (user_id, achievement_type, description, confidence_score)
                    VALUES (?, ?, ?, ?)
                """, (user_id, achievement_type, description, confidence))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Metrik güncelleme hatası: {e}")
    
    def update_personality_model(self, user_id, analysis):
        """Kişilik modelini güncelle"""
        try:
            # Mevcut modeli al
            if user_id not in self.personality_models:
                self.personality_models[user_id] = {}
            
            model = self.personality_models[user_id]
            
            # Yeni verileri entegre et
            for trait, value in analysis['personality_traits'].items():
                if trait in model:
                    # Öğrenme oranı ile güncelle
                    learning_rate = 0.1
                    model[trait] = model[trait] * (1 - learning_rate) + value * learning_rate
                else:
                    model[trait] = value
            
            # Güven skorlarını artır
            for trait in model:
                if trait in analysis['personality_traits']:
                    model[f"{trait}_confidence"] = min(1.0, model.get(f"{trait}_confidence", 0.5) + 0.1)
            
            print(f"🎯 Kullanıcı {user_id} kişilik modeli güncellendi!")
            
        except Exception as e:
            print(f"❌ Kişilik modeli hatası: {e}")
    
    def update_response_quality(self, user_id, message, bot_response, feedback):
        """Yanıt kalitesini değerlendir ve öğren"""
        try:
            quality_score = 0.5  # Varsayılan
            
            # Kullanıcı geri bildiriminden öğren
            feedback_lower = feedback.lower() if feedback else ""
            
            if any(word in feedback_lower for word in ['harika', 'süper', 'mükemmel', 'çok iyi']):
                quality_score = 0.9
            elif any(word in feedback_lower for word in ['iyi', 'güzel', 'fena değil']):
                quality_score = 0.7
            elif any(word in feedback_lower for word in ['kötü', 'berbat', 'anlamamış']):
                quality_score = 0.2
            
            # Öğrenmeyi kaydet
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO conversation_patterns 
                (user_id, pattern_type, pattern_value, effectiveness)
                VALUES (?, ?, ?, ?)
            """, (user_id, "response_quality", bot_response[:100], quality_score))
            
            db.commit()
            db.close()
            
            print(f"📈 Yanıt kalitesi güncellendi: {quality_score}")
            
        except Exception as e:
            print(f"❌ Kalite güncelleme hatası: {e}")
    
    def get_learning_summary(self, user_id):
        """Öğrenme özetini al"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Toplam öğrenme sayısı
            cursor.execute("""
                SELECT COUNT(*) FROM learning_achievements WHERE user_id = ?
            """, (user_id,))
            total_learnings = cursor.fetchone()[0]
            
            # En son öğrenilenler
            cursor.execute("""
                SELECT achievement_type, description, confidence_score, timestamp
                FROM learning_achievements WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT 5
            """, (user_id,))
            recent_learnings = cursor.fetchall()
            
            # Kişilik özeti
            cursor.execute("""
                SELECT trait_name, trait_value, confidence
                FROM user_personality WHERE user_id = ?
                ORDER BY confidence DESC LIMIT 3
            """, (user_id,))
            top_traits = cursor.fetchall()
            
            db.close()
            
            return {
                'total_learnings': total_learnings,
                'recent_learnings': recent_learnings,
                'top_personality_traits': top_traits
            }
            
        except Exception as e:
            print(f"❌ Öğrenme özeti hatası: {e}")
            return {}

# Global instance
super_learning = SuperLearningEngine()
