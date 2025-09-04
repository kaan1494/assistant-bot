"""
🔤 AKILLI YAZIM HATASI DÜZELTME MOTORU
Kullanıcının yazım hatalarını anlar ve düzeltir - Gerçek zeka!
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

class SmartTypoCorrector:
    """🔤 Akıllı Yazım Hatası Düzeltici - Gerçek AI gibi anlar"""
    
    def __init__(self):
        # Türkçe yaygın kelimeler ve varyasyonları
        self.common_words = {
            # Selamlaşmalar
            'naber': ['nabers', 'nabr', 'nber', 'nabrr', 'naer', 'nabeer'],
            'selam': ['slam', 'selm', 'salam', 'seelam', 'selem'],
            'merhaba': ['mraba', 'mrhaba', 'mehaba', 'meerhaba', 'merhba'],
            'iyi': ['iy', 'ii', 'iyii', 'yi'],
            'günaydın': ['gnaydın', 'günaydin', 'gunaydın', 'günaydinn'],
            
            # Yaygın kelimeler
            'nasıl': ['nasil', 'nasl', 'nasıll', 'nasıılsın'],
            'ne': ['nee', 'nnee', 'nne'],
            'var': ['varr', 'varr', 'vaar'],
            'yok': ['yokk', 'yook', 'yyok'],
            'tamam': ['tmam', 'taamam', 'tamaam', 'tmmam'],
            'evet': ['eveet', 'evt', 'evett', 'eevet'],
            'hayır': ['hayir', 'hayr', 'hayırr', 'hyr'],
            'çok': ['cok', 'çook', 'çokk', 'coook'],
            'teşekkür': ['tesekkur', 'teşekkürr', 'tşk', 'tşkr', 'sağol'],
            'güzel': ['guzel', 'güzell', 'gzel', 'güüzel'],
            'kötü': ['kotu', 'kötüü', 'ktü'],
            'iyi': ['ii', 'iyii', 'yi', 'iy'],
            
            # Zamanlar
            'bugün': ['bugun', 'bügun', 'bugünn', 'buügün'],
            'yarın': ['yarin', 'yarinn', 'yarrın'],
            'dün': ['dun', 'dünn', 'ddün'],
            'şimdi': ['simdi', 'şimdii', 'şmdii'],
            'sonra': ['snra', 'sonraa', 'soonra'],
            
            # Sorular
            'nedir': ['ndir', 'nedi', 'nedirr', 'neediir'],
            'nerede': ['nrde', 'nerede', 'nerdee'],
            'nasıl': ['nasl', 'nasill', 'nasıll'],
            'ne': ['nee', 'nne', 'nnee'],
            'kim': ['kimm', 'kiim', 'kkım'],
            
            # İşlemler
            'yap': ['yapp', 'yaap', 'yp'],
            'gel': ['gell', 'geel', 'gl'],
            'git': ['gitt', 'giit', 'gt'],
            'al': ['all', 'aal'],
            'ver': ['verr', 'veer', 'vr'],
            'bak': ['bakk', 'baak', 'bk'],
            'oku': ['okuu', 'ooku', 'ok'],
            'yaz': ['yazz', 'yaaz', 'yz'],
            
            # Duygular
            'mutlu': ['mtlu', 'mutluu', 'muutlu'],
            'üzgün': ['uzgun', 'üzgünn', 'üüzgün'],
            'kızgın': ['kizgin', 'kızgınn', 'kıızgın'],
            'mutluyum': ['mtluyum', 'mutluyumm', 'muutluyum'],
            'üzgünüm': ['uzgunum', 'üzgünümm', 'üüzgünüm'],
            
            # Teknoloji
            'bilgisayar': ['blgsyr', 'bilgisayarr', 'biilgisayar'],
            'telefon': ['tlfn', 'telefonn', 'teelefon'],
            'internet': ['intrnt', 'internett', 'iinternet'],
            'program': ['prgrm', 'programm', 'proogram'],
            
            # Bitcoin vb
            'bitcoin': ['btc', 'bitcoinn', 'biitcoin', 'bitcooin'],
            'dolar': ['dlr', 'dolarr', 'doolar'],
            'euro': ['euroo', 'eero', 'eurro'],
            
            # Yardım
            'yardım': ['yardim', 'yardımm', 'yaardım'],
            'help': ['heelp', 'helpp', 'hlp'],
            'anlat': ['anlatt', 'anllat', 'aanlat'],
            'göster': ['goster', 'gösterr', 'göözter'],
            
            # Kısaltmalar ve internetçe
            'tmm': ['tamam', 'tamamm', 'taaam'],
            'slm': ['selam', 'selamm', 'seeelam'],
            'mrb': ['merhaba', 'merhabaa', 'meerhaba'],
            'byz': ['bye', 'bay', 'güle güle'],
            'thx': ['thanks', 'teşekkür', 'sağol'],
            'ok': ['tamam', 'evet', 'olur'],
            'pls': ['please', 'lütfen', 'lütfenn'],
            'wtf': ['ne bu', 'bu ne', 'anlamadım'],
            'lol': ['haha', 'güldüm', 'komik'],
            'btw': ['bu arada', 'ayrıca'],
            'omg': ['aman tanrım', 'vay be'],
            'asap': ['acil', 'hemen', 'çabuk'],
            'fyi': ['bilgin olsun', 'haberiniz olsun'],
            'imo': ['bence', 'kanımca'],
            'tbh': ['dürüst olmak gerekirse', 'açıkçası']
        }
        
        # Yaygın yazım hataları
        self.common_typos = {
            'ş': ['s', 'ss'],
            'ç': ['c', 'cc'], 
            'ğ': ['g', 'gg'],
            'ü': ['u', 'uu'],
            'ö': ['o', 'oo'],
            'ı': ['i', 'ii'],
            'İ': ['I', 'i']
        }
    
    def correct_message(self, message: str) -> Tuple[str, Dict]:
        """📝 Mesajdaki yazım hatalarını düzelt"""
        
        original_message = message
        corrections = {}
        words = message.lower().split()
        corrected_words = []
        
        for word in words:
            # Noktalama işaretlerini ayır
            clean_word = re.sub(r'[^\w]', '', word)
            punctuation = re.findall(r'[^\w]', word)
            
            # En iyi eşleşmeyi bul
            corrected_word = self._find_best_match(clean_word)
            
            if corrected_word != clean_word:
                corrections[clean_word] = corrected_word
            
            # Noktalama işaretlerini geri ekle
            final_word = corrected_word
            if punctuation:
                final_word += ''.join(punctuation)
            
            corrected_words.append(final_word)
        
        corrected_message = ' '.join(corrected_words)
        
        return corrected_message, corrections
    
    def _find_best_match(self, word: str) -> str:
        """🔍 Kelime için en iyi eşleşmeyi bul"""
        
        if len(word) < 2:
            return word
            
        # Doğrudan sözlükte var mı?
        for correct_word, variants in self.common_words.items():
            if word == correct_word:
                return word
            if word in variants:
                return correct_word
        
        # Benzerlik analizi
        best_match = word
        best_score = 0.6  # Minimum benzerlik skoru
        
        for correct_word, variants in self.common_words.items():
            # Ana kelime ile karşılaştır
            score = self._similarity_score(word, correct_word)
            if score > best_score:
                best_match = correct_word
                best_score = score
            
            # Varyantlar ile karşılaştır
            for variant in variants:
                score = self._similarity_score(word, variant)
                if score > best_score:
                    best_match = correct_word
                    best_score = score
        
        # Türkçe karakter düzeltmeleri
        if best_match == word:
            best_match = self._fix_turkish_chars(word)
        
        return best_match
    
    def _similarity_score(self, word1: str, word2: str) -> float:
        """📊 İki kelime arasındaki benzerlik skoru"""
        
        # Tamamen aynı
        if word1 == word2:
            return 1.0
        
        # Uzunluk farkı çok fazlaysa
        if abs(len(word1) - len(word2)) > max(len(word1), len(word2)) * 0.5:
            return 0.0
        
        # SequenceMatcher kullan
        matcher = SequenceMatcher(None, word1, word2)
        base_score = matcher.ratio()
        
        # Başlangıç karakterleri aynıysa bonus
        if word1[0] == word2[0]:
            base_score += 0.1
        
        # Uzunluk bonusu/cezası
        length_diff = abs(len(word1) - len(word2))
        length_penalty = length_diff * 0.05
        
        final_score = base_score - length_penalty
        return max(0, min(1, final_score))
    
    def _fix_turkish_chars(self, word: str) -> str:
        """🇹🇷 Türkçe karakter hatalarını düzelt"""
        
        # Yaygın Türkçe karakter hataları
        replacements = {
            'ş': 's', 'Ş': 'S',
            'ç': 'c', 'Ç': 'C', 
            'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U',
            'ö': 'o', 'Ö': 'O',
            'ı': 'i', 'I': 'İ'
        }
        
        # Reverse mapping de dene
        reverse_replacements = {v: k for k, v in replacements.items()}
        
        # Her iki yönde de dene
        for original, replacement in replacements.items():
            if replacement in word:
                test_word = word.replace(replacement, original)
                # Bu düzeltme daha iyi bir eşleşme veriyorsa kullan
                for correct_word in self.common_words.keys():
                    if test_word == correct_word or test_word in self.common_words.get(correct_word, []):
                        return test_word
        
        return word
    
    def get_intent_from_corrected(self, corrected_message: str) -> str:
        """🎯 Düzeltilmiş mesajdan intent çıkar"""
        
        msg_lower = corrected_message.lower()
        
        # Selamlaşma
        if any(word in msg_lower for word in ['naber', 'selam', 'merhaba', 'iyi']):
            return 'selamlaşma'
        
        # Soru
        if any(word in msg_lower for word in ['nedir', 'nerede', 'nasıl', 'ne', 'kim']):
            return 'soru'
        
        # Finansal
        if any(word in msg_lower for word in ['bitcoin', 'dolar', 'euro', 'fiyat']):
            return 'araştırma'
        
        # Yardım
        if any(word in msg_lower for word in ['yardım', 'help', 'anlat', 'göster']):
            return 'yardım'
        
        # Duygusal
        if any(word in msg_lower for word in ['mutlu', 'üzgün', 'kızgın', 'mutluyum', 'üzgünüm']):
            return 'duygusal'
        
        return 'genel'

# Test kodu
if __name__ == "__main__":
    corrector = SmartTypoCorrector()
    
    test_messages = [
        "nabers nasılsın",
        "btc bugün kaç dlr",
        "cok uzgunum bugun", 
        "slm mrb naslsn",
        "yardim etrmisn",
        "tmm anlayım şmdi"
    ]
    
    for msg in test_messages:
        corrected, corrections = corrector.correct_message(msg)
        intent = corrector.get_intent_from_corrected(corrected)
        print(f"📨 '{msg}' → '{corrected}' [{intent}] {corrections}")
