"""
Akıllı araştırma sistemi
- Otomatik soru tespiti
- Uzun cümle analizi
- Gelişmiş arama
"""
import re
from research_helper import smart_search

def detect_question_type(text: str) -> tuple[bool, str]:
    """
    Verilen metnin soru/araştırma talebi olup olmadığını tespit eder
    Returns: (is_question, search_query)
    """
    text = text.lower().strip()
    
    # Soru kalıpları
    question_patterns = [
        (r"(.+)\s+nedir\?*$", "nedir"),
        (r"(.+)\s+nasıl\s+(.+)\?*$", "nasıl"),
        (r"(.+)\s+ne\s+demek\?*$", "ne demek"),
        (r"(.+)\s+hakkında\s+(.+)\?*$", "hakkında"),
        (r"(.+)\s+kimdir\?*$", "kimdir"),
        (r"(.+)\s+niçin\s+(.+)\?*$", "niçin"),
        (r"(.+)\s+neden\s+(.+)\?*$", "neden"),
        (r"(.+)\s+hangi\s+(.+)\?*$", "hangi"),
        (r"(.+)\s+ne\s+zaman\s+(.+)\?*$", "ne zaman"),
        (r"(.+)\s+gelecek\s+(.+)\?*$", "gelecek"),
        (r"(.+)\s+son\s+günler.+", "son günler"),
        (r"(.+)\s+son\s+zamanlarda.+", "son zamanlarda"),
        (r"(.+)\s+güncel\s+(.+)", "güncel"),
        (r"(.+)\s+araştır.+", "araştır"),
    ]
    
    # Soru kalıplarını kontrol et
    for pattern, question_type in question_patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            # Ana konuyu çıkar
            main_topic = match.group(1).strip()
            return True, clean_search_query(main_topic)
    
    # Uzun cümle kontrolü (15+ karakter ve komut değil)
    is_long_sentence = (
        len(text) > 15 and 
        not text.startswith(("not al", "hatırlat", "belge", "ara ", "aç ", "youtube"))
    )
    
    if is_long_sentence:
        return True, clean_search_query(text)
    
    return False, ""

def clean_search_query(text: str) -> str:
    """Arama sorgusunu temizle"""
    # Gereksiz kelimeleri kaldır
    cleanup_words = [
        "nedir", "nasıl", "ne demek", "hakkında", "bilgi", "ver", 
        "kimdir", "neden", "niçin", "hangi", "ne zaman", "araştır",
        "öğren", "anlat", "açıkla", "?", ".", "!", "gelmiş", "olduğu",
        "noktaları", "noktalarını", "durumu", "durumunu"
    ]
    
    result = text
    for word in cleanup_words:
        result = result.replace(word, " ")
    
    # Çoklu boşlukları temizle
    result = " ".join(result.split())
    return result.strip()

async def smart_research(update, text: str) -> bool:
    """
    Akıllı araştırma yap
    Returns: True if research was performed, False otherwise
    """
    is_question, search_query = detect_question_type(text)
    
    if not is_question:
        return False
    
    print(f"🔍 AKILLI ARAŞTIRMA: '{text}' → '{search_query}'")
    
    await update.message.reply_text("🤔 Bu bir soru/araştırma talebi gibi görünüyor, araştırıyorum...")
    
    try:
        results = smart_search(search_query)
        print(f"DEBUG: Akıllı araştırma - {len(results)} sonuç bulundu")
        
        if not results:
            await update.message.reply_text("❌ Bu konuda bilgi bulunamadı.")
            return True
        
        # İlk sonucu özetleyerek gönder
        source, content = results[0]
        await update.message.reply_text(f"💡 **{source}** kaynağından:")
        
        # İlk 2000 karakteri al (özet)
        summary = content[:2000] + "..." if len(content) > 2000 else content
        await update.message.reply_text(summary)
        
        # Eğer birden fazla kaynak varsa bilgilendir
        if len(results) > 1:
            await update.message.reply_text(
                f"📚 Toplam {len(results)} kaynakta bilgi bulundu. "
                f"Daha fazlası için 'ara {search_query}' yazabilirsin."
            )
        
        return True
        
    except Exception as e:
        print(f"DEBUG: Akıllı araştırma hatası: {e}")
        await update.message.reply_text(f"❌ Araştırma sırasında hata: {e}")
        return True

def test_question_detection():
    """Test fonksiyonu"""
    test_cases = [
        "bitcoin nedir?",
        "yapay zekanın son günlerde gelmiş olduğu noktaları araştır",
        "blockchain nasıl çalışır",
        "satoshi nakamoto kimdir",
        "not al test",
        "kısa",
        "güncel kripto para durumu"
    ]
    
    print("🧪 Soru tespit sistemi test ediliyor:")
    for case in test_cases:
        is_q, query = detect_question_type(case)
        print(f"  '{case}' → {is_q} → '{query}'")

if __name__ == "__main__":
    test_question_detection()
