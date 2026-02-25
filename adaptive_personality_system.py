"""
ADAPTİF KİŞİLİK SİSTEMİ
Her kullanıcıya özel kişilik geliştiren, konuşma tarzını adapte eden süper zeka
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict
import math

class AdaptivePersonalitySystem:
    """Her kullanıcıya özel kişilik geliştiren sistem"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.user_personalities = {}
        self.personality_templates = self.load_personality_templates()
        self.adaptive_responses = {}
        
        print("🎭 ADAPTİF KİŞİLİK SİSTEMİ aktif!")
    
    def load_personality_templates(self):
        """Kişilik şablonlarını yükle"""
        return {
            'formal_professional': {
                'greeting_style': 'formal',
                'language_tone': 'professional',
                'emoji_usage': 'minimal',
                'response_length': 'detailed',
                'politeness_level': 'high'
            },
            'friendly_casual': {
                'greeting_style': 'warm',
                'language_tone': 'casual',
                'emoji_usage': 'frequent',
                'response_length': 'moderate',
                'politeness_level': 'medium'
            },
            'supportive_empathetic': {
                'greeting_style': 'caring',
                'language_tone': 'warm',
                'emoji_usage': 'emotional',
                'response_length': 'comprehensive',
                'politeness_level': 'high'
            },
            'analytical_logical': {
                'greeting_style': 'direct',
                'language_tone': 'analytical',
                'emoji_usage': 'rare',
                'response_length': 'structured',
                'politeness_level': 'medium'
            },
            'enthusiastic_energetic': {
                'greeting_style': 'excited',
                'language_tone': 'energetic',
                'emoji_usage': 'abundant',
                'response_length': 'dynamic',
                'politeness_level': 'medium'
            },
            'wise_thoughtful': {
                'greeting_style': 'respectful',
                'language_tone': 'thoughtful',
                'emoji_usage': 'selective',
                'response_length': 'reflective',
                'politeness_level': 'high'
            }
        }
    
    def analyze_user_personality_preferences(self, user_id, message, conversation_history):
        """Kullanıcının kişilik tercihlerini analiz et"""
        preferences = {
            'communication_style': self.detect_communication_style(message, conversation_history),
            'interaction_preference': self.detect_interaction_preference(message),
            'emotional_needs': self.detect_emotional_needs(message),
            'information_processing': self.detect_information_processing(message),
            'social_distance': self.detect_social_distance(message, conversation_history),
            'response_expectations': self.detect_response_expectations(message)
        }
        
        # Tercihleri kullanıcı profiline kaydet
        self.update_user_personality_profile(user_id, preferences)
        
        return preferences
    
    def detect_communication_style(self, message, conversation_history):
        """İletişim tarzını tespit et"""
        message_lower = message.lower()
        style_indicators = {
            'formal': 0,
            'casual': 0,
            'direct': 0,
            'indirect': 0
        }
        
        # Formal göstergeler
        formal_words = ['sayın', 'saygılarımla', 'müsaade', 'rica ederim', 'lütfen', 'teşekkür ederim']
        style_indicators['formal'] = sum(1 for word in formal_words if word in message_lower)
        
        # Casual göstergeler
        casual_words = ['selam', 'naber', 'ya', 'işte', 'falan', 'böyle', 'şey']
        style_indicators['casual'] = sum(1 for word in casual_words if word in message_lower)
        
        # Direkt göstergeler
        if len(message.split()) < 10 and '?' in message:
            style_indicators['direct'] += 2
        
        # İndirekt göstergeler
        indirect_phrases = ['sanırım', 'galiba', 'belki', 'eğer mümkünse']
        style_indicators['indirect'] = sum(1 for phrase in indirect_phrases if phrase in message_lower)
        
        return max(style_indicators.items(), key=lambda x: x[1])[0]
    
    def detect_interaction_preference(self, message):
        """Etkileşim tercihi tespit et"""
        message_lower = message.lower()
        
        # Hızlı yanıt tercihi
        if any(word in message_lower for word in ['hemen', 'çabuk', 'kısa', 'özetle']):
            return 'quick_response'
        
        # Detaylı açıklama tercihi
        if any(word in message_lower for word in ['detay', 'ayrıntı', 'kapsamlı', 'tam']):
            return 'detailed_explanation'
        
        # Sohbet tercihi
        if any(word in message_lower for word in ['sohbet', 'konuş', 'anlat', 'dinle']):
            return 'conversational'
        
        # Problem çözme tercihi
        if any(word in message_lower for word in ['çöz', 'yardım', 'rehber', 'nasıl']):
            return 'problem_solving'
        
        return 'balanced'
    
    def detect_emotional_needs(self, message):
        """Duygusal ihtiyaçları tespit et"""
        message_lower = message.lower()
        emotional_needs = []
        
        # Destek ihtiyacı
        if any(word in message_lower for word in ['üzgün', 'stres', 'endişe', 'kaygı']):
            emotional_needs.append('emotional_support')
        
        # Onay ihtiyacı
        if any(phrase in message_lower for phrase in ['doğru mu', 'haklı mıyım', 'ne dersin']):
            emotional_needs.append('validation')
        
        # Güven ihtiyacı
        if any(word in message_lower for word in ['güvenilir', 'emin', 'kesin']):
            emotional_needs.append('reassurance')
        
        # Empati ihtiyacı
        if any(word in message_lower for word in ['anla', 'hisset', 'empati']):
            emotional_needs.append('empathy')
        
        return emotional_needs if emotional_needs else ['general_positivity']
    
    def detect_information_processing(self, message):
        """Bilgi işleme tarzını tespit et"""
        message_lower = message.lower()
        
        # Görsel öğrenme
        if any(word in message_lower for word in ['göster', 'örnek', 'resim', 'şema']):
            return 'visual'
        
        # Analitik işleme
        if any(word in message_lower for word in ['analiz', 'sebep', 'mantık', 'neden']):
            return 'analytical'
        
        # Adım adım işleme
        if any(word in message_lower for word in ['adım', 'sıra', 'önce', 'sonra']):
            return 'sequential'
        
        # Genel bakış
        if any(word in message_lower for word in ['genel', 'özet', 'ana', 'temel']):
            return 'holistic'
        
        return 'balanced'
    
    def detect_social_distance(self, message, conversation_history):
        """Sosyal mesafeyi tespit et"""
        message_lower = message.lower()
        
        # Yakın mesafe göstergeleri
        close_indicators = ['arkadaş', 'dost', 'buddy', 'sen', 'seni', 'birlikte']
        close_score = sum(1 for word in close_indicators if word in message_lower)
        
        # Uzak mesafe göstergeleri
        distant_indicators = ['siz', 'sizin', 'efendim', 'sayın']
        distant_score = sum(1 for word in distant_indicators if word in message_lower)
        
        # Konuşma geçmişi
        conversation_count = len(conversation_history) if conversation_history else 0
        
        if conversation_count > 10 or close_score > distant_score:
            return 'close'
        elif distant_score > close_score:
            return 'formal'
        else:
            return 'neutral'
    
    def detect_response_expectations(self, message):
        """Yanıt beklentilerini tespit et"""
        message_lower = message.lower()
        expectations = []
        
        # Hızlı yanıt beklentisi
        if any(word in message_lower for word in ['acil', 'hemen', 'şimdi']):
            expectations.append('speed')
        
        # Doğruluk beklentisi
        if any(word in message_lower for word in ['kesin', 'doğru', 'güvenilir']):
            expectations.append('accuracy')
        
        # Kişisellik beklentisi
        if any(word in message_lower for word in ['bana', 'benim', 'özel']):
            expectations.append('personalization')
        
        # Yaratıcılık beklentisi
        if any(word in message_lower for word in ['yaratıcı', 'farklı', 'özgün']):
            expectations.append('creativity')
        
        return expectations if expectations else ['standard']
    
    def update_user_personality_profile(self, user_id, preferences):
        """Kullanıcı kişilik profilini güncelle"""
        if user_id not in self.user_personalities:
            self.user_personalities[user_id] = {
                'primary_template': None,
                'customizations': {},
                'adaptation_history': [],
                'confidence_scores': {},
                'last_updated': datetime.now()
            }
        
        profile = self.user_personalities[user_id]
        
        # Tercihleri profilde güncelle
        for category, preference in preferences.items():
            if category not in profile['customizations']:
                profile['customizations'][category] = {}
            
            if isinstance(preference, list):
                for pref in preference:
                    profile['customizations'][category][pref] = profile['customizations'][category].get(pref, 0) + 1
            else:
                profile['customizations'][category][preference] = profile['customizations'][category].get(preference, 0) + 1
        
        # Ana template'i belirle
        profile['primary_template'] = self.determine_best_template(profile['customizations'])
        
        # Güven skorlarını güncelle
        self.update_confidence_scores(user_id)
        
        profile['last_updated'] = datetime.now()
        
        # Veritabanına kaydet
        self.save_personality_profile(user_id, profile)
    
    def determine_best_template(self, customizations):
        """En uygun kişilik şablonunu belirle"""
        template_scores = {}
        
        for template_name, template in self.personality_templates.items():
            score = 0
            
            # İletişim tarzı uyumu
            comm_style = customizations.get('communication_style', {})
            if 'formal' in comm_style and template_name in ['formal_professional', 'wise_thoughtful']:
                score += comm_style['formal'] * 2
            elif 'casual' in comm_style and template_name in ['friendly_casual', 'enthusiastic_energetic']:
                score += comm_style['casual'] * 2
            
            # Etkileşim tercihi uyumu
            interaction = customizations.get('interaction_preference', {})
            if 'detailed_explanation' in interaction and template_name in ['analytical_logical', 'wise_thoughtful']:
                score += interaction['detailed_explanation']
            elif 'quick_response' in interaction and template_name in ['friendly_casual', 'enthusiastic_energetic']:
                score += interaction['quick_response']
            
            template_scores[template_name] = score
        
        return max(template_scores.items(), key=lambda x: x[1])[0] if template_scores else 'friendly_casual'
    
    def update_confidence_scores(self, user_id):
        """Güven skorlarını güncelle"""
        profile = self.user_personalities[user_id]
        customizations = profile['customizations']
        
        for category, preferences in customizations.items():
            total_interactions = sum(preferences.values())
            for preference, count in preferences.items():
                confidence = min(1.0, count / max(1, total_interactions))
                profile['confidence_scores'][f"{category}_{preference}"] = confidence
    
    def save_personality_profile(self, user_id, profile):
        """Kişilik profilini veritabanına kaydet"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30)
            cursor = db.cursor()
            
            # JSON olarak kaydet
            profile_json = json.dumps(profile, default=str)
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_personality_profiles 
                (user_id, profile_data, last_updated)
                VALUES (?, ?, ?)
            """, (user_id, profile_json, datetime.now()))
            
            # Tablo yoksa oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_personality_profiles (
                    user_id INTEGER PRIMARY KEY,
                    profile_data TEXT,
                    last_updated TIMESTAMP
                )
            """)
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Kişilik profili kaydetme hatası: {e}")
    
    def generate_adaptive_response(self, user_id, message, base_response, context=None):
        """Adaptif yanıt üret"""
        try:
            # Kullanıcı profilini al
            if user_id not in self.user_personalities:
                # Varsayılan profil oluştur
                self.user_personalities[user_id] = {
                    'primary_template': 'friendly_casual',
                    'customizations': {},
                    'confidence_scores': {}
                }
            
            profile = self.user_personalities[user_id]
            template = self.personality_templates[profile['primary_template']]
            
            # Yanıtı şablona göre uyarla
            adapted_response = self.apply_personality_template(base_response, template, profile)
            
            # Bağlama göre ek düzenlemeler
            if context:
                adapted_response = self.apply_contextual_adaptations(adapted_response, context, profile)
            
            return adapted_response
            
        except Exception as e:
            print(f"❌ Adaptif yanıt üretme hatası: {e}")
            return base_response
    
    def apply_personality_template(self, response, template, user_profile):
        """Kişilik şablonunu yanıta uygula"""
        adapted = response
        
        # Selamlama tarzı
        greeting_style = template['greeting_style']
        if greeting_style == 'formal':
            adapted = adapted.replace('Merhaba', 'Sayın kullanıcım, merhabalar')
            adapted = adapted.replace('Selam', 'İyi günler')
        elif greeting_style == 'warm':
            adapted = adapted.replace('Merhaba', 'Merhaba canım! 😊')
        elif greeting_style == 'excited':
            adapted = adapted.replace('Merhaba', 'Selaaaam! 🎉✨')
        elif greeting_style == 'caring':
            adapted = adapted.replace('Merhaba', 'Merhaba sevgili dostum 💙')
        
        # Emoji kullanımı
        emoji_usage = template['emoji_usage']
        if emoji_usage == 'minimal':
            # Emojileri kaldır
            import re
            adapted = re.sub(r'[😀-🙏🎉💙✨🔥💫🎯📚🤖⚡🧠]', '', adapted)
        elif emoji_usage == 'frequent':
            # Daha fazla emoji ekle
            adapted = adapted.replace('.', ' 😊')
            adapted = adapted.replace('!', '! 🎉')
        elif emoji_usage == 'abundant':
            # Bol emoji
            adapted = f"✨ {adapted} ✨"
            adapted = adapted.replace('harika', 'harika 🔥')
            adapted = adapted.replace('güzel', 'güzel 💫')
        
        # Dil tonu
        language_tone = template['language_tone']
        if language_tone == 'professional':
            adapted = adapted.replace('çok iyi', 'mükemmel')
            adapted = adapted.replace('süper', 'oldukça başarılı')
        elif language_tone == 'energetic':
            adapted = adapted.replace('iyi', 'SÜPER İYİ!')
            adapted = adapted.replace('güzel', 'MÜKEMMEL!')
        elif language_tone == 'warm':
            adapted = adapted.replace('size', 'size sevgili dostum')
            adapted = adapted.replace('yardımcı olabilirim', 'yanınızdayım')
        
        # Nezaket seviyesi
        politeness_level = template['politeness_level']
        if politeness_level == 'high':
            if not any(word in adapted.lower() for word in ['lütfen', 'rica', 'teşekkür']):
                adapted += "\n\nRica ederim, başka bir konuda yardımcı olabilir miyim?"
        
        return adapted
    
    def apply_contextual_adaptations(self, response, context, user_profile):
        """Bağlamsal uyarlamaları uygula"""
        adapted = response
        
        # Duygusal durum
        if context.get('emotional_state'):
            primary_emotion = context['emotional_state'].get('primary_emotion')
            
            if primary_emotion == 'sadness':
                adapted = f"💙 {adapted}\n\nSizin için buradayım. Bu zor anları birlikte aşacağız."
            elif primary_emotion == 'anger':
                adapted = f"😌 {adapted}\n\nBir nefes alalım. Her şeyi çözeriz, merak etmeyin."
            elif primary_emotion == 'happiness':
                adapted = f"🎉 {adapted}\n\nEnerjiniz çok güzel! Ben de mutlu oldum."
            elif primary_emotion == 'worry':
                adapted = f"🤗 {adapted}\n\nEndişelerinizi anlıyorum. Adım adım hallederiz."
        
        # Aciliyet seviyesi
        if context.get('urgency_level', 0) > 0.7:
            adapted = f"⚡ HEMEN: {adapted}"
        
        # Bilgi arama türü
        if context.get('knowledge_seeking'):
            knowledge_type = context['knowledge_seeking'].get('type')
            if knowledge_type == 'deep_learning':
                adapted += "\n\n📚 Size daha kapsamlı bilgi vermek isterseniz, sormaktan çekinmeyin!"
        
        return adapted
    
    def learn_from_feedback(self, user_id, message, response, user_reaction):
        """Kullanıcı geri bildiriminden öğren"""
        try:
            if user_id not in self.user_personalities:
                return
            
            profile = self.user_personalities[user_id]
            
            # Geri bildirim analizi
            reaction_lower = user_reaction.lower() if user_reaction else ""
            
            if any(word in reaction_lower for word in ['harika', 'mükemmel', 'çok iyi', 'beğendim']):
                # Pozitif geri bildirim - mevcut yaklaşımı güçlendir
                self.reinforce_current_approach(user_id)
            elif any(word in reaction_lower for word in ['kötü', 'beğenmedim', 'yanlış', 'böyle değil']):
                # Negatif geri bildirim - yaklaşımı değiştir
                self.adjust_approach(user_id)
            
            # Adaptasyon geçmişine ekle
            profile['adaptation_history'].append({
                'timestamp': datetime.now(),
                'message': message[:100],
                'response_style': profile['primary_template'],
                'user_reaction': user_reaction,
                'effectiveness': self.calculate_effectiveness(user_reaction)
            })
            
            # Son 20 girdiyi tut
            if len(profile['adaptation_history']) > 20:
                profile['adaptation_history'] = profile['adaptation_history'][-20:]
            
        except Exception as e:
            print(f"❌ Geri bildirim öğrenme hatası: {e}")
    
    def reinforce_current_approach(self, user_id):
        """Mevcut yaklaşımı güçlendir"""
        profile = self.user_personalities[user_id]
        current_template = profile['primary_template']
        
        # Güven skorunu artır
        template_key = f"template_{current_template}"
        profile['confidence_scores'][template_key] = min(1.0, 
            profile['confidence_scores'].get(template_key, 0.5) + 0.1)
    
    def adjust_approach(self, user_id):
        """Yaklaşımı ayarla"""
        profile = self.user_personalities[user_id]
        current_template = profile['primary_template']
        
        # Alternatif template dene
        alternative_templates = [name for name in self.personality_templates.keys() 
                               if name != current_template]
        
        if alternative_templates:
            # En az kullanılan template'i seç
            usage_scores = {}
            for template in alternative_templates:
                template_key = f"template_{template}"
                usage_scores[template] = profile['confidence_scores'].get(template_key, 0.0)
            
            new_template = min(usage_scores.items(), key=lambda x: x[1])[0]
            profile['primary_template'] = new_template
            
            print(f"🔄 Kullanıcı {user_id} için kişilik şablonu {new_template} olarak değiştirildi")
    
    def calculate_effectiveness(self, user_reaction):
        """Etkililik skorunu hesapla"""
        if not user_reaction:
            return 0.5
        
        reaction_lower = user_reaction.lower()
        
        if any(word in reaction_lower for word in ['harika', 'mükemmel', 'süper', 'çok iyi']):
            return 1.0
        elif any(word in reaction_lower for word in ['iyi', 'güzel', 'fena değil']):
            return 0.7
        elif any(word in reaction_lower for word in ['kötü', 'berbat', 'yanlış']):
            return 0.1
        else:
            return 0.5
    
    def get_personality_summary(self, user_id):
        """Kişilik özetini al"""
        if user_id not in self.user_personalities:
            return "Henüz kişilik profili oluşturulmamış."
        
        profile = self.user_personalities[user_id]
        template = profile['primary_template']
        
        # İnsan dostu açıklama
        template_descriptions = {
            'formal_professional': 'Profesyonel ve resmi',
            'friendly_casual': 'Samimi ve rahat',
            'supportive_empathetic': 'Destekleyici ve empatik',
            'analytical_logical': 'Analitik ve mantıklı',
            'enthusiastic_energetic': 'Enerjik ve coşkulu',
            'wise_thoughtful': 'Bilge ve düşünceli'
        }
        
        description = template_descriptions.get(template, 'Dengeli')
        
        summary = f"""🎭 **KİŞİLİK PROFİLİNİZ**

📋 **Ana Tarz:** {description}
🎯 **Güven Seviyesi:** {len(profile.get('confidence_scores', {})) * 10}%
📅 **Son Güncelleme:** {profile.get('last_updated', 'Bilinmiyor')}
🔄 **Adaptasyon Sayısı:** {len(profile.get('adaptation_history', []))}

💡 **Özellikler:**
• Size özel yanıt tarzı geliştirdim
• Her konuşmada sizi daha iyi anlıyorum
• Tercihlerinize göre kendimi ayarlıyorum"""
        
        return summary

# Global instance
adaptive_personality = AdaptivePersonalitySystem()
