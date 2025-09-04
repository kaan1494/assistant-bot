"""
Gelişmiş araştırma sistemi - Wikipedia, web scraping ve bilgi toplama
"""
import requests
import wikipediaapi
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import json

# Wikipedia API setup
wiki_wiki = wikipediaapi.Wikipedia(
    language='tr',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent='TelegramAssistant/1.0 (https://example.com/contact)'
)

def search_wikipedia(query, max_chars=2000):
    """Wikipedia'da arama yap"""
    try:
        # Önce arama yap
        search_results = requests.get(
            "https://tr.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 3
            },
            timeout=10
        ).json()
        
        if not search_results.get("query", {}).get("search"):
            return None, "Wikipedia'da sonuç bulunamadı."
        
        # İlk sonucu al
        first_result = search_results["query"]["search"][0]
        title = first_result["title"]
        
        # Sayfayı getir
        page = wiki_wiki.page(title)
        if not page.exists():
            return None, f"'{title}' sayfası bulunamadı."
        
        # Özet oluştur
        summary = page.summary[:max_chars]
        
        content = f"# {title}\n\n"
        content += f"**Wikipedia Özeti:**\n{summary}\n\n"
        content += f"**Kaynak:** {page.fullurl}\n"
        
        return content, f"Wikipedia'da '{title}' hakkında bilgi bulundu."
        
    except Exception as e:
        return None, f"Wikipedia hatası: {e}"

def search_web_modern(query, max_chars=1500):
    """Modern web araması - DuckDuckGo Instant Answer API"""
    try:
        # DuckDuckGo Instant Answer API
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            },
            timeout=10
        )
        
        data = response.json()
        content = f"# Web Araması: {query}\n\n"
        
        # Abstract (özet) varsa ekle
        if data.get("Abstract"):
            content += f"**Özet:** {data['Abstract']}\n\n"
            
        # Definition (tanım) varsa ekle  
        if data.get("Definition"):
            content += f"**Tanım:** {data['Definition']}\n\n"
            
        # Answer (cevap) varsa ekle
        if data.get("Answer"):
            content += f"**Cevap:** {data['Answer']}\n\n"
            
        # Related topics (ilgili konular)
        if data.get("RelatedTopics"):
            content += "**İlgili Konular:**\n"
            for topic in data["RelatedTopics"][:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    content += f"- {topic['Text'][:100]}...\n"
        
        # İçerik varsa döndür
        if len(content) > 50:
            return content[:max_chars], "Web araması tamamlandı."
        else:
            return None, "Web'de yeterli bilgi bulunamadı."
            
    except Exception as e:
        return None, f"Web araması hatası: {e}"

def search_news(query, max_items=5):
    """Basit haber araması"""
    try:
        # NewsAPI alternatif - RSS kullanımı
        rss_sources = [
            "https://www.haberturk.com/rss",
            "https://www.sozcu.com.tr/feed/"
        ]
        
        content = f"# Haber Araması: {query}\n\n"
        found_news = False
        
        for rss_url in rss_sources:
            try:
                response = requests.get(rss_url, timeout=5)
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')[:max_items]
                
                for item in items:
                    title = item.title.text if item.title else ""
                    description = item.description.text if item.description else ""
                    
                    # Query ile eşleşme kontrolü
                    if query.lower() in (title + description).lower():
                        content += f"**{title}**\n{description[:200]}...\n\n"
                        found_news = True
                        
            except:
                continue
                
        if found_news:
            return content, "Haber araması tamamlandı."
        else:
            return None, "İlgili haber bulunamadı."
            
    except Exception as e:
        return None, f"Haber araması hatası: {e}"

def smart_search(query):
    """Akıllı arama - önce Wikipedia, sonra web"""
    results = []
    
    # 1. Wikipedia araması
    wiki_content, wiki_msg = search_wikipedia(query)
    if wiki_content:
        results.append(("📚 Wikipedia", wiki_content))
    
    # 2. Web araması  
    web_content, web_msg = search_web_modern(query)
    if web_content:
        results.append(("🌐 Web", web_content))
    
    # 3. Haber araması (belirli kelimeler için)
    news_keywords = ["haber", "gündem", "son", "bugün", "olay"]
    if any(keyword in query.lower() for keyword in news_keywords):
        news_content, news_msg = search_news(query)
        if news_content:
            results.append(("📰 Haberler", news_content))
    
    return results
