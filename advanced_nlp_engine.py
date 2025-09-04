"""
GELİŞMİŞ NLP VE ANLAMA SİSTEMİ
Kullanıcı mesajlarını derin düzeyde analiz eden, bağlamı kavrayan, 
ironiyi, duygusal tonları ve gizli anlamları anlayan süper zeka
"""

import re
import sqlite3
from datetime import datetime
from collections import defaultdict
import math

class AdvancedNLPEngine:
    """Gelişmiş doğal dil işleme motoru"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.context_memory = {}  # Konuşma bağlamı hafızası
        self.semantic_patterns = {}  # Anlamsal kalıplar
        self.user_language_models = {}  # Kullanıcı dil modelleri
        
        print("🧠 GELİŞMİŞ NLP MOTORU aktif!")
    
    def deep_understand_message(self, user_id, message, conversation_history=[]):
        """Mesajı derinlemesine anla"""
        understanding = {
            'literal_meaning': self.extract_literal_meaning(message),
            'implied_meaning': self.extract_implied_meaning(message),
            'emotional_tone': self.analyze_emotional_tone(message),
            'intent_analysis': self.analyze_complex_intent(message),
            'context_awareness': self.analyze_context(message, conversation_history),
            'sarcasm_detection': self.detect_sarcasm(message),
            'urgency_level': self.assess_urgency(message),
            'politeness_level': self.assess_politeness(message),
            'knowledge_seeking': self.detect_knowledge_seeking(message),
            'relationship_building': self.detect_relationship_building(message)
        }
        
        # Kullanıcı dil modelini güncelle
        self.update_user_language_model(user_id, message, understanding)
        
        return understanding
    
    def extract_literal_meaning(self, message):
        """Kelimesi kelimesine anlamı çıkar"""
        literal = {
            'main_subjects': self.extract_subjects(message),
            'actions': self.extract_actions(message),
            'objects': self.extract_objects(message),
            'time_references': self.extract_time_references(message),
            'location_references': self.extract_location_references(message),
            'quantities': self.extract_quantities(message)
        }
        return literal
    
    def extract_subjects(self, message):
        """Özne(ler)i çıkar"""
        subjects = []
        message_lower = message.lower()
        
        # Kişi zamirleri
        pronouns = ['ben', 'sen', 'o', 'biz', 'siz', 'onlar']
        for pronoun in pronouns:
            if pronoun in message_lower:
                subjects.append(pronoun)
        
        # İsimler (büyük harfle başlayan kelimeler)
        words = message.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                subjects.append(word.lower())
        
        return list(set(subjects))
    
    def extract_actions(self, message):
        """Eylem(ler)i çıkar"""
        actions = []
        message_lower = message.lower()
        
        # Yaygın fiiller
        common_verbs = [
            'git', 'gel', 'yap', 'et', 'ol', 'ver', 'al', 'bul', 'öğren',
            'anlat', 'söyle', 'görüş', 'konuş', 'çalış', 'oku', 'yaz',
            'ara', 'bak', 'dinle', 'izle', 'düşün', 'plan', 'organize'
        ]
        
        for verb in common_verbs:
            if verb in message_lower:
                actions.append(verb)
        
        return list(set(actions))
    
    def extract_objects(self, message):
        """Nesne(ler)i çıkar"""
        objects = []
        message_lower = message.lower()
        
        # Yaygın nesneler
        common_objects = [
            'iş', 'ev', 'okul', 'telefon', 'bilgisayar', 'araba', 'kitap',
            'film', 'müzik', 'oyun', 'proje', 'plan', 'randevu', 'toplantı'
        ]
        
        for obj in common_objects:
            if obj in message_lower:
                objects.append(obj)
        
        return list(set(objects))
    
    def extract_time_references(self, message):
        """Zaman referanslarını çıkar"""
        time_refs = []
        message_lower = message.lower()
        
        # Zaman ifadeleri
        time_expressions = [
            'şimdi', 'bugün', 'yarın', 'dün', 'sabah', 'öğle', 'akşam', 'gece',
            'hafta', 'ay', 'yıl', 'geçen', 'gelecek', 'önce', 'sonra',
            'erken', 'geç', 'hemen', 'çabuk', 'yavaş'
        ]
        
        for expr in time_expressions:
            if expr in message_lower:
                time_refs.append(expr)
        
        # Saat formatları
        time_pattern = r'(\d{1,2}):(\d{2})'
        time_matches = re.findall(time_pattern, message)
        for match in time_matches:
            time_refs.append(f"{match[0]}:{match[1]}")
        
        return time_refs
    
    def extract_location_references(self, message):
        """Lokasyon referanslarını çıkar"""
        locations = []
        message_lower = message.lower()
        
        location_words = [
            'burada', 'orada', 'şurada', 'evde', 'işte', 'okulda',
            'dışarıda', 'içeride', 'yukarıda', 'aşağıda', 'yakında', 'uzakta'
        ]
        
        for loc in location_words:
            if loc in message_lower:
                locations.append(loc)
        
        return locations
    
    def extract_quantities(self, message):
        """Miktarları çıkar"""
        quantities = []
        
        # Sayılar
        number_pattern = r'\d+'
        numbers = re.findall(number_pattern, message)
        quantities.extend(numbers)
        
        # Miktar belirten kelimeler
        quantity_words = ['çok', 'az', 'biraz', 'fazla', 'yeterli', 'eksik', 'tam']
        message_lower = message.lower()
        for word in quantity_words:
            if word in message_lower:
                quantities.append(word)
        
        return quantities
    
    def extract_implied_meaning(self, message):
        """Ima edilen anlamı çıkar"""
        implied = {
            'hidden_requests': self.detect_hidden_requests(message),
            'emotional_subtext': self.detect_emotional_subtext(message),
            'social_cues': self.detect_social_cues(message),
            'unstated_assumptions': self.detect_assumptions(message)
        }
        return implied
    
    def detect_hidden_requests(self, message):
        """Gizli istekleri tespit et"""
        hidden_requests = []
        message_lower = message.lower()
        
        # Dolaylı rica kalıpları
        indirect_patterns = [
            ('yardıma ihtiyacım var', 'help_request'),
            ('bilmiyorum', 'information_request'),
            ('nasıl yapacağımı bilmiyorum', 'guidance_request'),
            ('zor durumdayım', 'support_request'),
            ('sıkıldım', 'entertainment_request'),
            ('yalnızım', 'companionship_request')
        ]
        
        for pattern, request_type in indirect_patterns:
            if pattern in message_lower:
                hidden_requests.append(request_type)
        
        return hidden_requests
    
    def detect_emotional_subtext(self, message):
        """Duygusal alt metni tespit et"""
        subtext = {}
        message_lower = message.lower()
        
        # Endişe belirtileri
        worry_indicators = ['umarım', 'sanırım', 'galiba', 'belki', 'emin değilim']
        if any(indicator in message_lower for indicator in worry_indicators):
            subtext['uncertainty'] = 0.7
        
        # Hayal kırıklığı
        disappointment_indicators = ['ama', 'fakat', 'yine', 'gene', 'hep böyle']
        if any(indicator in message_lower for indicator in disappointment_indicators):
            subtext['disappointment'] = 0.6
        
        # Heyecan gizleme
        excitement_indicators = ['sadece', 'basit', 'önemli değil']
        if any(indicator in message_lower for indicator in excitement_indicators):
            # Çelişkili duygu - heyecanı gizleme
            subtext['hidden_excitement'] = 0.5
        
        return subtext
    
    def detect_social_cues(self, message):
        """Sosyal ipuçlarını tespit et"""
        social_cues = []
        message_lower = message.lower()
        
        # Sınır koyma
        if any(phrase in message_lower for phrase in ['zamanım yok', 'meşgulüm', 'başka zaman']):
            social_cues.append('boundary_setting')
        
        # Yakınlık kurma
        if any(phrase in message_lower for phrase in ['sen de', 'biz', 'birlikte', 'paylaş']):
            social_cues.append('closeness_seeking')
        
        # Onay arama
        if message.count('değil mi') > 0 or 'doğru mu' in message_lower:
            social_cues.append('approval_seeking')
        
        return social_cues
    
    def detect_assumptions(self, message):
        """Varsayımları tespit et"""
        assumptions = []
        message_lower = message.lower()
        
        # Bilgi varsayımları
        if any(phrase in message_lower for phrase in ['biliyorsun', 'tabii ki', 'elbette']):
            assumptions.append('shared_knowledge')
        
        # Durum varsayımları
        if any(phrase in message_lower for phrase in ['her zaman', 'genelde', 'normal']):
            assumptions.append('typical_situation')
        
        return assumptions
    
    def analyze_emotional_tone(self, message):
        """Duygusal tonu analiz et"""
        tone = {
            'primary_emotion': None,
            'intensity': 0.0,
            'mixed_emotions': [],
            'emotional_progression': None
        }
        
        message_lower = message.lower()
        
        # Duygu göstergeleri ve şiddetleri
        emotion_indicators = {
            'happiness': (['mutlu', 'sevinç', 'harika', 'süper', 'mükemmel'], [1.0, 0.9, 0.8, 0.7, 0.9]),
            'sadness': (['üzgün', 'kötü', 'mutsuz', 'depresif'], [0.8, 0.6, 0.7, 0.9]),
            'anger': (['sinir', 'kızgın', 'öfke', 'deliriyorum'], [0.7, 0.8, 0.9, 1.0]),
            'fear': (['korku', 'endişe', 'kaygı', 'tedirgin'], [0.8, 0.6, 0.7, 0.5]),
            'surprise': (['şaşır', 'inanamıyorum', 'hayret'], [0.6, 0.8, 0.7]),
            'disgust': (['iğrenç', 'tiksinç', 'berbat'], [0.8, 0.9, 0.7])
        }
        
        detected_emotions = {}
        for emotion, (words, intensities) in emotion_indicators.items():
            emotion_score = 0
            for i, word in enumerate(words):
                if word in message_lower:
                    emotion_score = max(emotion_score, intensities[i])
            if emotion_score > 0:
                detected_emotions[emotion] = emotion_score
        
        if detected_emotions:
            # En güçlü duygu
            primary = max(detected_emotions.items(), key=lambda x: x[1])
            tone['primary_emotion'] = primary[0]
            tone['intensity'] = primary[1]
            
            # Karışık duygular
            tone['mixed_emotions'] = [(emotion, score) for emotion, score in detected_emotions.items() 
                                    if emotion != primary[0] and score > 0.3]
        
        return tone
    
    def analyze_complex_intent(self, message):
        """Karmaşık niyet analizi"""
        intent = {
            'primary_intent': None,
            'secondary_intents': [],
            'intent_confidence': 0.0,
            'intent_complexity': 'simple'
        }
        
        message_lower = message.lower()
        
        # Gelişmiş intent kalıpları
        intent_patterns = {
            'information_seeking': [
                'nedir', 'nasıl', 'ne zaman', 'nerede', 'kim', 'hangi',
                'bilgi ver', 'açıkla', 'anlat', 'öğrenmek istiyorum'
            ],
            'help_requesting': [
                'yardım', 'destek', 'destekle', 'rehberlik', 'tavsiye',
                'öner', 'söyle ne yapayım', 'ne yapmalı'
            ],
            'social_interaction': [
                'sohbet', 'konuş', 'dinle', 'paylaş', 'anla', 'empati'
            ],
            'task_delegation': [
                'yap', 'organize et', 'planla', 'ayarla', 'hazırla', 'düzenle'
            ],
            'emotional_support': [
                'üzgün', 'stresli', 'endişeli', 'rahatla', 'sakinleş'
            ],
            'creative_collaboration': [
                'birlikte', 'fikir', 'yaratıcı', 'kreatif', 'hayal et'
            ]
        }
        
        intent_scores = {}
        for intent_type, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent_type] = score / len(keywords)
        
        if intent_scores:
            # Ana intent
            primary = max(intent_scores.items(), key=lambda x: x[1])
            intent['primary_intent'] = primary[0]
            intent['intent_confidence'] = primary[1]
            
            # İkincil intentler
            intent['secondary_intents'] = [(intent_type, score) for intent_type, score in intent_scores.items() 
                                         if intent_type != primary[0] and score > 0.2]
            
            # Karmaşıklık seviyesi
            if len(intent_scores) > 2:
                intent['intent_complexity'] = 'complex'
            elif len(intent_scores) > 1:
                intent['intent_complexity'] = 'moderate'
        
        return intent
    
    def analyze_context(self, message, conversation_history):
        """Bağlam analizi"""
        context = {
            'references_to_previous': [],
            'conversation_flow': None,
            'topic_continuity': 0.0,
            'relationship_status': 'new'
        }
        
        if not conversation_history:
            return context
        
        message_lower = message.lower()
        
        # Önceki mesajlara referanslar
        reference_words = ['bu', 'o', 'şu', 'dediğin', 'söylediğin', 'bahsettiğin']
        for word in reference_words:
            if word in message_lower:
                context['references_to_previous'].append(word)
        
        # Konuşma akışı
        if len(conversation_history) > 0:
            last_message = conversation_history[-1][0].lower()
            
            # Soruya cevap mı?
            if '?' in last_message and any(word in message_lower for word in ['evet', 'hayır', 'tabii', 'bilmem']):
                context['conversation_flow'] = 'answering_question'
            
            # Konuya devam mı?
            common_words = set(message_lower.split()) & set(last_message.split())
            if len(common_words) > 2:
                context['topic_continuity'] = len(common_words) / len(set(message_lower.split()))
        
        # İlişki durumu
        if len(conversation_history) > 10:
            context['relationship_status'] = 'established'
        elif len(conversation_history) > 3:
            context['relationship_status'] = 'developing'
        
        return context
    
    def detect_sarcasm(self, message):
        """Sarkazm tespiti"""
        sarcasm_score = 0.0
        message_lower = message.lower()
        
        # Sarkazm göstergeleri
        sarcasm_patterns = [
            ('tabii canım', 0.9),
            ('çok güzel', 0.6),  # Bağlama bağlı
            ('harika ya', 0.7),
            ('süper be', 0.8),
            ('ne kadar zekice', 0.8),
            ('bravo', 0.5),  # Bağlama bağlı
            ('aynen', 0.4)   # Bağlama bağlı
        ]
        
        for pattern, score in sarcasm_patterns:
            if pattern in message_lower:
                sarcasm_score = max(sarcasm_score, score)
        
        # Aşırı pozitif kelimelerle negatif bağlam
        positive_words = ['mükemmel', 'harika', 'süper', 'muhteşem']
        negative_context = ['ama', 'fakat', 'ancak', 'yine de']
        
        has_positive = any(word in message_lower for word in positive_words)
        has_negative_context = any(word in message_lower for word in negative_context)
        
        if has_positive and has_negative_context:
            sarcasm_score = max(sarcasm_score, 0.7)
        
        return {
            'is_sarcastic': sarcasm_score > 0.5,
            'confidence': sarcasm_score,
            'indicators': []  # Tespit edilen göstergeler
        }
    
    def assess_urgency(self, message):
        """Aciliyet seviyesini değerlendir"""
        urgency_score = 0.0
        message_lower = message.lower()
        
        # Acil kelimeler
        urgent_words = ['acil', 'hemen', 'çabuk', 'derhal', 'ivedi', 'şimdi', 'bekleyemez']
        urgency_score += sum(0.2 for word in urgent_words if word in message_lower)
        
        # Büyük harf kullanımı
        if message.isupper():
            urgency_score += 0.3
        elif any(word.isupper() for word in message.split()):
            urgency_score += 0.1
        
        # Ünlem işaretleri
        urgency_score += min(0.3, message.count('!') * 0.1)
        
        # Tekrarlanan kelimeler
        words = message_lower.split()
        repeated_words = [word for word in set(words) if words.count(word) > 1]
        if repeated_words:
            urgency_score += 0.1
        
        return min(1.0, urgency_score)
    
    def assess_politeness(self, message):
        """Nezaket seviyesini değerlendir"""
        politeness_score = 0.5  # Nötr başlangıç
        message_lower = message.lower()
        
        # Nezaket göstergeleri
        polite_words = ['lütfen', 'rica ederim', 'teşekkür', 'sağol', 'mersi', 'pardon', 'özür']
        politeness_score += sum(0.1 for word in polite_words if word in message_lower)
        
        # Saygılı hitap
        respectful_address = ['sayın', 'değerli', 'sevgili']
        if any(word in message_lower for word in respectful_address):
            politeness_score += 0.2
        
        # Kaba kelimeler (azaltıcı)
        rude_words = ['sus', 'kapa', 'salak', 'aptal', 'hadi be']
        politeness_score -= sum(0.2 for word in rude_words if word in message_lower)
        
        return max(0.0, min(1.0, politeness_score))
    
    def detect_knowledge_seeking(self, message):
        """Bilgi arama davranışını tespit et"""
        knowledge_seeking = {
            'is_seeking': False,
            'type': None,
            'specificity': 'general',
            'depth_level': 'surface'
        }
        
        message_lower = message.lower()
        
        # Bilgi arama kalıpları
        if any(word in message_lower for word in ['nedir', 'nasıl', 'ne zaman', 'nerede', 'kim', 'hangi']):
            knowledge_seeking['is_seeking'] = True
            knowledge_seeking['type'] = 'factual'
        
        if any(phrase in message_lower for phrase in ['öğrenmek istiyorum', 'merak ediyorum', 'bilmek istiyorum']):
            knowledge_seeking['is_seeking'] = True
            knowledge_seeking['type'] = 'learning'
        
        # Spesifiklik
        if len(message.split()) > 10:
            knowledge_seeking['specificity'] = 'specific'
        
        # Derinlik seviyesi
        if any(word in message_lower for word in ['detay', 'ayrıntı', 'derinlemesine', 'kapsamlı']):
            knowledge_seeking['depth_level'] = 'deep'
        
        return knowledge_seeking
    
    def detect_relationship_building(self, message):
        """İlişki kurma davranışını tespit et"""
        relationship_building = {
            'is_building': False,
            'type': None,
            'openness_level': 0.0
        }
        
        message_lower = message.lower()
        
        # Kişisel paylaşım
        personal_sharing = ['ben', 'benim', 'bana', 'kendim', 'hayatım', 'ailem']
        if any(word in message_lower for word in personal_sharing):
            relationship_building['is_building'] = True
            relationship_building['type'] = 'personal_sharing'
            relationship_building['openness_level'] = 0.6
        
        # Empati kurma
        empathy_words = ['anlıyorum', 'hissediyorum', 'anlarım', 'empati']
        if any(word in message_lower for word in empathy_words):
            relationship_building['is_building'] = True
            relationship_building['type'] = 'empathy'
            relationship_building['openness_level'] = 0.7
        
        # Soru sorma (karşıdakine ilgi)
        if '?' in message and any(word in message_lower for word in ['sen', 'siz', 'sizin']):
            relationship_building['is_building'] = True
            relationship_building['type'] = 'interest_in_other'
            relationship_building['openness_level'] = 0.5
        
        return relationship_building
    
    def update_user_language_model(self, user_id, message, understanding):
        """Kullanıcı dil modelini güncelle"""
        if user_id not in self.user_language_models:
            self.user_language_models[user_id] = {
                'vocabulary_complexity': 0.0,
                'sentence_structure': 'simple',
                'emotional_expressiveness': 0.0,
                'directness': 0.5,
                'formality': 0.5,
                'conversation_count': 0
            }
        
        model = self.user_language_models[user_id]
        model['conversation_count'] += 1
        
        # Kelime karmaşıklığı
        complex_words = [word for word in message.split() if len(word) > 6]
        complexity_score = len(complex_words) / len(message.split()) if message.split() else 0
        model['vocabulary_complexity'] = (model['vocabulary_complexity'] + complexity_score) / 2
        
        # Duygusal ifade
        emotion_intensity = understanding['emotional_tone']['intensity']
        model['emotional_expressiveness'] = (model['emotional_expressiveness'] + emotion_intensity) / 2
        
        # Doğrudanlık
        directness = 1.0 - len(understanding['implied_meaning']['hidden_requests']) * 0.2
        model['directness'] = (model['directness'] + directness) / 2
        
        print(f"🔄 Kullanıcı {user_id} dil modeli güncellendi!")
    
    def generate_context_aware_response(self, user_id, understanding, base_response):
        """Bağlam bilincinde yanıt üret"""
        try:
            enhanced_response = base_response
            
            # Duygusal tona uygun yanıt
            primary_emotion = understanding['emotional_tone']['primary_emotion']
            if primary_emotion == 'sadness':
                enhanced_response = f"💙 {enhanced_response}\n\nBurada sizin için varım, endişelenmeyin."
            elif primary_emotion == 'happiness':
                enhanced_response = f"😊 {enhanced_response}\n\nEnerjiniz çok güzel!"
            elif primary_emotion == 'anger':
                enhanced_response = f"😌 {enhanced_response}\n\nNefes alın, birlikte çözeriz."
            
            # Sarkazm tespiti
            if understanding['sarcasm_detection']['is_sarcastic']:
                enhanced_response += "\n\n😏 Sanırım burada biraz ironi var... Doğru anladım mı?"
            
            # Aciliyet seviyesi
            if understanding['urgency_level'] > 0.7:
                enhanced_response = f"⚡ HEMEN: {enhanced_response}"
            
            # Nezaket seviyesine uyum
            politeness = understanding['politeness_level']
            if politeness > 0.8:
                enhanced_response += "\n\nSaygılarımla 🙏"
            elif politeness < 0.3:
                enhanced_response = enhanced_response.replace('lütfen', '').replace('rica ederim', '')
            
            # Bilgi arama davranışı
            if understanding['knowledge_seeking']['is_seeking']:
                if understanding['knowledge_seeking']['depth_level'] == 'deep':
                    enhanced_response += "\n\n📚 Size daha detaylı bilgi verebilirim, istiyorsanız!"
            
            # İlişki kurma
            if understanding['relationship_building']['is_building']:
                enhanced_response += "\n\n💫 Sizi daha iyi tanımaya başlıyorum!"
            
            return enhanced_response
            
        except Exception as e:
            print(f"❌ Bağlam bilincinde yanıt hatası: {e}")
            return base_response

# Global instance
advanced_nlp = AdvancedNLPEngine()
