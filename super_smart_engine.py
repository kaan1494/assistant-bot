"""
🧠 SÜPER ZEKİ MOTOR - ChatGPT ve Claude seviyesinde akıllı bot!
✨ Gerçek AI gibi konuşan, anlayan ve öğrenen sistem
"""

import re
import datetime
from datetime import datetime, timedelta
import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any

class SuperSmartEngine:
    """🧠 ChatGPT/Claude seviyesinde SÜPER ZEKİ MOTOR"""
    
    def __init__(self, db_path="data/assistant.db"):
        self.db_path = db_path
        self.current_date = datetime.now()
        self.context_memory = {}  # Konuşma bağlamı bellegi
        self.user_preferences = {}  # Kullanıcı tercihleri
        
    def smart_date_parser(self, text: str, reference_date: datetime = None) -> Optional[datetime]:
        """🎯 SÜPER AKILLI TARİH ÇÖZÜCÜsü - GPT seviyesinde!"""
        if not reference_date:
            reference_date = datetime.now()
            
        text = text.lower().strip()
        
        # 📅 1. GÖRECELI TARİHLER - "2 gün sonra", "yarın" vs
        relative_patterns = {
            # Günler
            r'(\d+)\s*gün\s*sonra': lambda m: reference_date + timedelta(days=int(m.group(1))),
            r'(\d+)\s*hafta\s*sonra': lambda m: reference_date + timedelta(weeks=int(m.group(1))),
            r'(\d+)\s*ay\s*sonra': lambda m: self._add_months(reference_date, int(m.group(1))),
            
            # Sabit günler
            r'yarın': lambda m: reference_date + timedelta(days=1),
            r'bugün': lambda m: reference_date,
            r'öbür\s*gün': lambda m: reference_date + timedelta(days=2),
            r'gelecek\s*hafta': lambda m: reference_date + timedelta(weeks=1),
            r'gelecek\s*ay': lambda m: self._add_months(reference_date, 1),
        }
        
        for pattern, func in relative_patterns.items():
            match = re.search(pattern, text)
            if match:
                return func(match)
        
        # 📅 2. AY İÇİ TARİHLER - "ayın 15'inde", "bu ayın 20'sinde"
        month_patterns = [
            r'(?:bu\s*)?ayın\s*(\d+)(?:\'?[ıi]nde|\.|\s|$)',
            r'ayın\s*(\d+)(?:\.|\s|$)',
            r'(\d+)(?:\'?[ıi]nde|\s*[.]\s*)',
        ]
        
        for pattern in month_patterns:
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                if 1 <= day <= 31:
                    try:
                        target_date = reference_date.replace(day=day)
                        # Eğer geçmişse bir sonraki ay
                        if target_date < reference_date:
                            target_date = self._add_months(target_date, 1)
                        return target_date
                    except ValueError:
                        # Geçersiz gün (örn: 31 Şubat)
                        continue
        
        # 📅 3. TAM TARİH FORMATLARI - "05.09.2025", "5/9/2025"
        date_patterns = [
            r'(\d{1,2})[./-](\d{1,2})[./-](\d{4})',  # DD.MM.YYYY
            r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})',  # YYYY.MM.DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                parts = [int(x) for x in match.groups()]
                
                # Format tahmin etme
                if parts[0] > 31:  # YYYY-MM-DD format
                    year, month, day = parts
                else:  # DD-MM-YYYY format
                    day, month, year = parts
                    
                try:
                    return datetime(year, month, day)
                except ValueError:
                    continue
        
        # 📅 4. GÜNÜN ADLARI - "pazartesi", "cuma"
        weekdays = {
            'pazartesi': 0, 'salı': 1, 'çarşamba': 2, 'perşembe': 3,
            'cuma': 4, 'cumartesi': 5, 'pazar': 6
        }
        
        for day_name, weekday in weekdays.items():
            if day_name in text:
                days_ahead = weekday - reference_date.weekday()
                if days_ahead <= 0:  # Geçmişse gelecek hafta
                    days_ahead += 7
                return reference_date + timedelta(days=days_ahead)
        
        return None
    
    def smart_context_analyzer(self, user_id: int, message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """🧠 BAĞLAM FARKINDALIĞI - Önceki konuşmaları hatırlar"""
        context = {
            'current_topic': None,
            'mentioned_dates': [],
            'mentioned_people': [],
            'ongoing_task': None,
            'user_mood': 'neutral',
            'conversation_flow': 'new',
            'needs_clarification': False,
            'assumed_context': {}
        }
        
        # Son 5 mesajı analiz et
        recent_messages = conversation_history[-5:] if conversation_history else []
        
        # Devam eden konuşma tespiti
        if recent_messages:
            last_bot_message = None
            for msg in reversed(recent_messages):
                if msg.get('is_bot', False):
                    last_bot_message = msg.get('content', '')
                    break
            
            # Bot soru sormuşsa ve kullanıcı cevaplıyorsa
            if last_bot_message and ('?' in last_bot_message or 'hangi' in last_bot_message.lower()):
                context['conversation_flow'] = 'answer_to_question'
                
                # Tarih sorusu mu sorulmuş?
                if any(word in last_bot_message.lower() for word in ['hangi ay', 'kaç', 'tarih']):
                    context['ongoing_task'] = 'date_clarification'
        
        # Bu ayın context'i - "15'inde" gibi eksik tarihlerde
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        if re.search(r'\d+[\'i]nde|ayın\s*\d+', message.lower()):
            context['assumed_context']['month'] = current_month
            context['assumed_context']['year'] = current_year
            context['needs_clarification'] = False  # Bu ayı varsay!
        
        return context
    
    def smart_response_generator(self, user_id: int, message: str, intent: str, 
                               context: Dict, conversation_history: List[Dict]) -> str:
        """🎯 AKILLI YANIT ÜRETİCİ - Claude/GPT gibi doğal"""
        
        # Kullanıcı kişiliğini hatırla
        user_personality = self._get_user_personality(user_id)
        
        # Bağlama göre yanıt stili
        if context['conversation_flow'] == 'answer_to_question':
            response_style = 'continuation'
        else:
            response_style = 'fresh_start'
        
        # Intent'e göre akıllı yanıt
        if intent == 'musaitlik':
            return self._generate_availability_response(message, context, user_personality)
        elif intent == 'not_alma':
            return self._generate_note_response(message, context, user_personality)
        elif intent == 'ajanda':
            return self._generate_schedule_response(message, context, user_personality)
        elif intent == 'sohbet':
            return self._generate_chat_response(message, context, user_personality, conversation_history)
        else:
            return self._generate_general_response(message, context, user_personality)
    
    def _generate_availability_response(self, message: str, context: Dict, personality: Dict) -> str:
        """📅 Müsaitlik kontrolü yanıtları"""
        # Tarih çıkar
        date = self.smart_date_parser(message)
        
        if not date and context.get('needs_clarification'):
            return "🤔 Hangi tarihi kastediyorsunuz? Bu ayın hangi günü veya tam tarih belirtir misiniz?"
        elif not date:
            # Bu ayı varsay
            day_match = re.search(r'(\d+)', message)
            if day_match:
                day = int(day_match.group(1))
                try:
                    date = datetime.now().replace(day=day)
                    if date < datetime.now():
                        date = self._add_months(date, 1)
                except ValueError:
                    return "🤔 Hangi tarihi kastediyorsunuz? Lütfen geçerli bir tarih belirtin."
        
        if date:
            date_str = date.strftime("%d %B %Y")
            return f"📅 **{date_str}** tarihine bakıyorum...\n\n💡 Gerçek müsaitlik kontrolü için veritabanı bağlantısı gerekiyor!"
        
        return "🤔 Tarih belirtir misiniz? Örnek: 'ayın 15'inde müsait miyim?' veya '05.09.2025 müsait miyim?'"
    
    def _generate_note_response(self, message: str, context: Dict, personality: Dict) -> str:
        """📝 Not alma yanıtları"""
        note_content = message.replace('not al:', '').replace('not al', '').strip()
        
        if not note_content:
            return "📝 Ne kaydetmemi istiyorsunuz? Örnek: 'not al: yarın toplantım var'"
        
        # Tarihi akıllıca çıkar
        date = self.smart_date_parser(note_content)
        
        if date:
            date_str = date.strftime("%d %B %Y")
            return f"✅ **Not kaydedildi!** 📝\n\n📅 **Tarih:** {date_str}\n📝 **İçerik:** {note_content}\n\n💡 Notlarınızı 'notlarımı göster' diyerek görüntüleyebilirsiniz!"
        else:
            return f"✅ **Not kaydedildi!** 📝\n\n📝 **İçerik:** {note_content}\n\n💡 Notlarınızı 'notlarımı göster' diyerek görüntüleyebilirsiniz!"
    
    def _generate_schedule_response(self, message: str, context: Dict, personality: Dict) -> str:
        """📅 Ajanda yanıtları"""
        date = self.smart_date_parser(message)
        
        if date:
            date_str = date.strftime("%d %B %Y")
            return f"📅 **Etkinlik planlandı!**\n\n📅 **Tarih:** {date_str}\n📝 **Detay:** {message}\n\n💡 Ajandanızı 'ajandamı göster' diyerek görüntüleyebilirsiniz!"
        else:
            return "📅 **Etkinlik kaydedildi!**\n\n💡 Daha kesin tarih belirtirseniz daha iyi planlama yapabilirim!"
    
    def _generate_chat_response(self, message: str, context: Dict, personality: Dict, history: List[Dict]) -> str:
        """💬 Doğal sohbet yanıtları - Claude/GPT gibi"""
        
        # Konuşmanın tonunu analiz et
        tone = self._analyze_message_tone(message)
        
        # Kişiliğe göre yanıt stili
        if personality.get('style', 'casual') == 'formal':
            greeting = "Size nasıl yardımcı olabilirim?"
        else:
            greeting = "Ne konuşmak istersiniz? 😊"
        
        # Önceki konuşmaya referans
        if history and len(history) > 2:
            return f"Devam edelim! 🚀 {greeting}\n\n💡 Son konuştuğumuz konulardan devam edebiliriz ya da yeni bir konu açabiliriz."
        else:
            return f"Merhaba! 👋 {greeting}\n\n🎯 Hangi konularda yardımcı olmamı istersiniz?"
    
    def _generate_general_response(self, message: str, context: Dict, personality: Dict) -> str:
        """🌟 Genel akıllı yanıtlar"""
        return "Anlıyorum! Size nasıl yardımcı olabilirim? 😊\n\n💡 Notlarınızı kaydetmek, müsaitliğinizi kontrol etmek veya sadece sohbet etmek için buradayım!"
    
    def _add_months(self, date: datetime, months: int) -> datetime:
        """📅 Ay ekleme yardımcısı"""
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, [31,29,31,30,31,30,31,31,30,31,30,31][month-1])
        return date.replace(year=year, month=month, day=day)
    
    def _get_user_personality(self, user_id: int) -> Dict:
        """👤 Kullanıcı kişiliği"""
        return self.user_preferences.get(user_id, {'style': 'casual', 'verbosity': 'medium'})
    
    def _analyze_message_tone(self, message: str) -> str:
        """🎭 Mesaj tonu analizi"""
        if any(word in message.lower() for word in ['üzgün', 'kötü', 'mutsuz', 'sorun']):
            return 'sad'
        elif any(word in message.lower() for word in ['harika', 'mükemmel', 'süper', 'güzel']):
            return 'happy'
        elif '!' in message or any(word in message.lower() for word in ['acil', 'hemen', 'çabuk']):
            return 'excited'
        else:
            return 'neutral'

    def generate_smart_response(self, user_id, message, context=None, personalized_context="", 
                              emotional_state=None, conversation_analysis=None):
        """🚀 Süper zeki yanıt üretimi - ChatGPT Pro seviyesi"""
        
        # Akıllı tarih algılama
        smart_date = self.smart_date_parser(message)
        
        # Bağlam analizi
        context_info = self.smart_context_analyzer(user_id, message, context)
        
        # Yanıt oluştur
        response = self.response_generator(
            message, context_info, smart_date, 
            personalized_context, emotional_state, conversation_analysis
        )
        
        return response
    
    def generate_smart_response(self, user_id, message, context=None, 
                              personalized_context="", emotional_state=None, 
                              conversation_analysis=None):
        """🧠 Süper akıllı yanıt üretimi - Ana metod"""
        
        try:
            # 1. Akıllı tarih analizi
            smart_date = self.smart_date_parser(message)
            
            # 2. Context analizi
            context_info = self.smart_context_analyzer(user_id, message, context)
            
            # 3. Yanıt üretimi
            response = self.response_generator(
                message, context_info, smart_date, 
                personalized_context, emotional_state, conversation_analysis
            )
            
            return response
            
        except Exception as e:
            print(f"❌ SuperSmartEngine hatası: {e}")
            return f"Anlıyorum ki '{message}' konusunda yardımcı olmaya çalışıyorsun. Size nasıl yardımcı olabilirim? 🤔"

# Test fonksiyonu
if __name__ == "__main__":
    engine = SuperSmartEngine()
    
    # Test mesajları
    test_messages = [
        "2 gün sonra müsait miyim",
        "ayın 15'inde toplantım var",
        "05.09.2025 tarihinde müsaitliyim kontrol et",
        "not al: yarın önemli görüşmem var"
    ]
    
    for msg in test_messages:
        date = engine.smart_date_parser(msg)
        print(f"📨 '{msg}' → 📅 {date}")
