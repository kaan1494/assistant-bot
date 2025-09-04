"""
🎭 DUYGUSAL ZEKA MOTORU - İnsan gibi empati ve anlayış
Kullanıcının duygularını anlar ve ona göre yanıt verir
"""

import re
import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

class EmotionalIntelligenceEngine:
    """🎭 Duygusal Zeka Motoru - İnsani empati ve anlayış"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.emotion_patterns = self._load_emotion_patterns()
        self.personality_types = self._load_personality_types()
        self.setup_database()
        
    def setup_database(self):
        """Duygusal zeka tabloları oluştur"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # Kullanıcı duygusal geçmiş
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_emotional_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    detected_emotion TEXT,
                    emotion_intensity REAL,
                    message_context TEXT,
                    response_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            db.commit()
            db.close()
            print("🎭 Duygusal zeka tabloları oluşturuldu!")
            
        except Exception as e:
            print(f"❌ Duygusal zeka tablo hatası: {e}")
        
    def _load_emotion_patterns(self) -> Dict:
        """Duygu kalıplarını yükle"""
        return {
            'joy': {
                'keywords': ['mutlu', 'sevinç', 'harika', 'mükemmel', 'süper', 'muhteşem'],
                'emojis': ['😊', '😄', '🎉', '😃', '🥳', '✨'],
                'phrases': ['çok mutluyum', 'ne güzel', 'harika haber'],
                'response_style': 'celebratory'
            },
            'sadness': {
                'keywords': ['üzgün', 'mutsuz', 'kötü', 'üzücü', 'depresif'],
                'emojis': ['😢', '😞', '😔', '💔', '😿'],
                'phrases': ['çok üzgünüm', 'kötü hissediyorum', 'moralsizim'],
                'response_style': 'supportive'
            },
            'anger': {
                'keywords': ['sinirli', 'kızgın', 'öfkeli', 'bıktım', 'nefret'],
                'emojis': ['😠', '😡', '🤬', '💢', '😤'],
                'phrases': ['çok sinirliyim', 'bıktım artık', 'dayanamıyorum'],
                'response_style': 'calming'
            },
            'anxiety': {
                'keywords': ['endişeli', 'kaygılı', 'korku', 'tedirgin', 'gergin'],
                'emojis': ['😰', '😨', '😟', '😧', '🥺'],
                'phrases': ['endişeliyim', 'korkuyorum', 'tedirginim'],
                'response_style': 'reassuring'
            },
            'excitement': {
                'keywords': ['heyecanlı', 'coşkulu', 'sabırsız', 'meraklı'],
                'emojis': ['🤩', '😍', '🔥', '⚡', '🚀'],
                'phrases': ['çok heyecanlıyım', 'sabırsızlanıyorum'],
                'response_style': 'energetic'
            },
            'confusion': {
                'keywords': ['karışık', 'anlamadım', 'şaşkın', 'belirsiz'],
                'emojis': ['😕', '🤔', '😵', '🤷'],
                'phrases': ['anlamadım', 'karıştım', 'emin değilim'],
                'response_style': 'clarifying'
            },
            'gratitude': {
                'keywords': ['teşekkür', 'minnettarım', 'sağol', 'mersi'],
                'emojis': ['🙏', '💝', '🤗', '❤️', '💕'],
                'phrases': ['çok teşekkürler', 'minnettarım', 'çok sağol'],
                'response_style': 'humble'
            }
        }
    
    def _load_personality_types(self) -> Dict:
        """Kişilik tiplerini yükle"""
        return {
            'formal': {'tone': 'professional', 'emoji_use': 'minimal'},
            'casual': {'tone': 'friendly', 'emoji_use': 'moderate'},
            'energetic': {'tone': 'enthusiastic', 'emoji_use': 'high'},
            'supportive': {'tone': 'caring', 'emoji_use': 'moderate'}
        }
    
    def analyze_emotional_state(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """🎭 Kullanıcının duygusal durumunu analiz et"""
        
        message_lower = message.lower()
        detected_emotions = {}
        
        # Her duygu için skor hesapla
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            
            # Anahtar kelimeler
            for keyword in patterns['keywords']:
                if keyword in message_lower:
                    score += 2
            
            # Emojiler
            for emoji in patterns['emojis']:
                if emoji in message:
                    score += 3
            
            # İfadeler
            for phrase in patterns['phrases']:
                if phrase in message_lower:
                    score += 4
            
            if score > 0:
                detected_emotions[emotion] = score
        
        # En baskın duyguyu bul
        primary_emotion = max(detected_emotions, key=detected_emotions.get) if detected_emotions else 'neutral'
        
        # Duygu yoğunluğunu belirle
        max_score = max(detected_emotions.values()) if detected_emotions else 0
        intensity = 'high' if max_score >= 6 else 'medium' if max_score >= 3 else 'low'
        
        # Geçmiş duygusal durum analizi
        emotional_trend = 'stable'  # Basitleştirdik
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_scores': detected_emotions,
            'intensity': intensity,
            'emotional_trend': emotional_trend,
            'needs_support': primary_emotion in ['sadness', 'anxiety', 'anger'],
            'response_style': self.emotion_patterns.get(primary_emotion, {}).get('response_style', 'neutral')
        }
    
    def generate_empathetic_response(self, emotional_analysis: Dict, message: str = "") -> str:
        """💝 Empatik yanıt üret"""
        
        emotion = emotional_analysis.get('primary_emotion', 'neutral')
        intensity = emotional_analysis.get('intensity', 'medium')
        response_style = emotional_analysis.get('response_style', 'neutral')
        
        # Duyguya göre yanıt geliştir
        if response_style == 'supportive':
            enhanced_response = self._create_supportive_response("", emotion, intensity)
        elif response_style == 'celebratory':
            enhanced_response = self._create_celebratory_response("", emotion, intensity)
        elif response_style == 'calming':
            enhanced_response = self._create_calming_response("", emotion, intensity)
        elif response_style == 'reassuring':
            enhanced_response = self._create_reassuring_response("", emotion, intensity)
        elif response_style == 'energetic':
            enhanced_response = self._create_energetic_response("", emotion, intensity)
        elif response_style == 'clarifying':
            enhanced_response = self._create_clarifying_response("", emotion, intensity)
        elif response_style == 'humble':
            enhanced_response = self._create_humble_response("", emotion, intensity)
        else:
            enhanced_response = "😊 Size yardımcı olmaktan mutluluk duyuyorum!"
        
        # Duygusal destek gerekiyorsa ekstra öneriler ekle
        if emotional_analysis.get('needs_support', False):
            enhanced_response = self._add_emotional_support(enhanced_response, emotion)
        
        return enhanced_response
    
    def _create_supportive_response(self, base_response: str, emotion: str, intensity: str) -> str:
        """🤗 Destekleyici yanıt oluştur"""
        
        support_intros = {
            'high': "🤗 Sizi çok iyi anlıyorum. Bu durumda olmak gerçekten zor olmalı.",
            'medium': "😊 Anlıyorum, bazen böyle hissedebiliriz.",
            'low': "😌 Anlıyorum."
        }
        
        return support_intros.get(intensity, support_intros['medium'])
    
    def _create_celebratory_response(self, base_response: str, emotion: str, intensity: str) -> str:
        """🎉 Kutlayıcı yanıt oluştur"""
        if intensity == 'high':
            return "Harika haber! Ne kadar mutlu olduğunuzu hissedebiliyorum! 🎉✨"
        else:
            return "Bu güzel! 😊🌟"
    
    def _create_calming_response(self, base_response: str, emotion: str, intensity: str) -> str:
        """😌 Sakinleştirici yanıt oluştur"""
        return "Derin bir nefes alalım. Her şey yoluna girecek. 🌸💙"
    
    def _create_reassuring_response(self, base_response: str, emotion: str, intensity: str) -> str:
        """🤗 Güven verici yanıt oluştur"""
        return "Endişelenmeyin, birlikte hallederiz. 🤗💪"
    
    def _create_energetic_response(self, base_response: str, emotion: str, intensity: str) -> str:
        """⚡ Enerjik yanıt oluştur"""
        return "Harika enerji! Bu heyecanı hissedebiliyorum! ⚡🚀"
    
    def _create_clarifying_response(self, base_response: str, emotion: str, intensity: str) -> str:
        """🤔 Açıklayıcı yanıt oluştur"""
        return "Anladığımdan emin olmak istiyorum. Doğru mu anladım? 🤔💭"
    
    def _create_humble_response(self, base_response: str, emotion: str, intensity: str) -> str:
        """🙏 Alçakgönüllü yanıt oluştur"""
        return "Teşekkür ederim, bu benim için çok değerli. 🙏✨"
    
    def _add_emotional_support(self, response: str, emotion: str) -> str:
        """💝 Ekstra duygusal destek ekle"""
        support_messages = {
            'sadness': "\n\nBu zor zamanlardan geçeceksiniz. İhtiyacınız olursa buradayım. 💙",
            'anxiety': "\n\nEndişenizin geçmesi için elimden geleni yapacağım. 🌈",
            'anger': "\n\nSinirli hissetmenizi anlıyorum. Beraber çözüm bulalım. 🕊️"
        }
        
        return response + support_messages.get(emotion, "\n\nSize yardımcı olmak için buradayım. 💝")

# Test kodu
if __name__ == "__main__":
    engine = EmotionalIntelligenceEngine()
    
    test_messages = [
        "Çok mutluyum bugün harika bir gün! 🎉",
        "Üzgünüm, bugün kötü haberler aldım 😢",
        "Çok sinirliyim, hiçbir şey yolunda gitmiyor! 😠",
        "Endişeliyim, yarınki sınav için çok kaygılıyım 😰"
    ]
    
    for msg in test_messages:
        print(f"\n📨 Mesaj: '{msg}'")
        emotional_state = engine.analyze_emotional_state(msg)
        response = engine.generate_empathetic_response(emotional_state, msg)
        print(f"🎭 Duygu: {emotional_state['primary_emotion']} ({emotional_state['intensity']})")
        print(f"💝 Yanıt: {response}")
