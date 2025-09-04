"""
Donanım Haber Yapay Zeka Haber Takipçisi
- 2 saatte bir kontrol
- Yeni haberleri tespit etme
- Telegram'da paylaşım
"""
import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime as dt
from pathlib import Path
import hashlib

# Veritabanı
BASE = Path(__file__).parent
DATA = BASE / "data"
DB_PATH = DATA / "assistant.db"

def init_news_db():
    """Haber veritabanını hazırla"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_news (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT UNIQUE,
            summary TEXT,
            image_url TEXT,
            publish_date TEXT,
            content_hash TEXT,
            source TEXT DEFAULT 'Unknown',
            created_at TEXT,
            sent_to_telegram BOOLEAN DEFAULT 0
        )
    """)
    
    # Mevcut tabloya source kolonu ekle (eğer yoksa)
    try:
        conn.execute("ALTER TABLE ai_news ADD COLUMN source TEXT DEFAULT 'Unknown'")
        conn.commit()
        print("📊 Veritabanı güncellendi: source kolonu eklendi")
    except:
        pass  # Kolon zaten varsa hata görmezden gel
    
    conn.commit()
    conn.close()

def fetch_ai_news():
    """Donanım Haber ve WebTekno'dan yapay zeka haberlerini çek"""
    all_news = []
    
    # 1) Donanım Haber'den haber çek
    try:
        donanimhaber_news = fetch_donanimhaber_news()
        all_news.extend(donanimhaber_news)
        print(f"✅ Donanım Haber: {len(donanimhaber_news)} haber")
    except Exception as e:
        print(f"❌ Donanım Haber hatası: {e}")
    
    # 2) WebTekno'dan haber çek
    try:
        webtekno_news = fetch_webtekno_news()
        all_news.extend(webtekno_news)
        print(f"✅ WebTekno: {len(webtekno_news)} haber")
    except Exception as e:
        print(f"❌ WebTekno hatası: {e}")
    
    return all_news

def fetch_donanimhaber_news():
    """Donanım Haber'den yapay zeka haberlerini çek"""
    try:
        url = "https://www.donanimhaber.com/yapay-zeka"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"🔍 Donanım Haber kontrol ediliyor: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Haber listesini bul
        news_items = []
        
        # Donanım Haber yapısına göre seçiciler (bu siteye özel)
        articles = soup.find_all('div', class_=['news-item', 'card-news', 'news-card']) or \
                  soup.find_all('article') or \
                  soup.find_all('div', class_=lambda x: x and 'news' in x.lower())
        
        if not articles:
            # Alternatif: tüm linkleri kontrol et
            articles = soup.find_all('a', href=True)
            articles = [a for a in articles if 'yapay-zeka' in a.get('href', '') or 'ai' in a.get('href', '').lower()]
        
        print(f"🔍 Donanım Haber: {len(articles)} potansiyel haber bulundu")
        
        for article in articles[:10]:  # İlk 10 haberi kontrol et (daha fazla seçenek)
            try:
                # Başlık ve link çıkar
                if article.name == 'a':
                    title = article.get_text(strip=True)
                    link = article.get('href')
                else:
                    title_elem = article.find('a') or article.find(['h1', 'h2', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href') if title_elem.name == 'a' else None
                
                if not title or not link:
                    continue
                
                # REKLAM/TANITIM FİLTRELERI - Bu içerikleri atla
                reklam_kelimeleri = [
                    'mobil uygulamamızı', 'uygulamamızı', 'dh mobil', 
                    'indirin', 'yükleyin', 'app store', 'google play',
                    'tanıtım', 'reklam', 'sponsor', 'duyuru',
                    'mobil uygulaması', 'uygulamasi', 'dh uygulaması'
                ]
                
                title_lower = title.lower()
                if any(kelime in title_lower for kelime in reklam_kelimeleri):
                    print(f"🚫 Reklam/tanıtım atlandı: {title[:50]}...")
                    continue
                
                # Tam URL oluştur
                if link.startswith('/'):
                    link = 'https://www.donanimhaber.com' + link
                elif not link.startswith('http'):
                    link = 'https://www.donanimhaber.com/' + link
                
                # Resim bul
                img_elem = article.find('img')
                image_url = None
                if img_elem:
                    image_url = img_elem.get('src') or img_elem.get('data-src')
                    if image_url and image_url.startswith('/'):
                        image_url = 'https://www.donanimhaber.com' + image_url
                
                # Özet bul
                summary = ""
                summary_elem = article.find(['p', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['summary', 'desc', 'excerpt']))
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)[:200]
                
                # Hash oluştur (benzersizlik için)
                content_hash = hashlib.md5((title + link).encode()).hexdigest()
                
                news_items.append({
                    'title': f"[Donanım Haber] {title}",
                    'url': link,
                    'summary': summary,
                    'image_url': image_url,
                    'content_hash': content_hash,
                    'publish_date': dt.datetime.now().isoformat(),
                    'source': 'Donanım Haber'
                })
                
                print(f"✅ Donanım Haber: {title[:50]}...")
                
            except Exception as e:
                print(f"❌ Donanım Haber haber işleme hatası: {e}")
                continue
        
        return news_items
        
    except Exception as e:
        print(f"❌ Donanım Haber site çekme hatası: {e}")
        return []

def fetch_webtekno_news():
    """WebTekno'dan yapay zeka haberlerini çek"""
    try:
        url = "https://www.webtekno.com/yapay-zeka"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"🔍 WebTekno kontrol ediliyor: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # WebTekno yapısına göre haber listesini bul
        news_items = []
        
        # WebTekno'nun haber linklerini bul
        # Site yapısına göre a taglarını kontrol et
        articles = soup.find_all('a', href=True)
        
        # Sadece haber linklerini filtrele (genellikle .html ile biter)
        news_links = []
        for link in articles:
            href = link.get('href', '')
            if (href.endswith('.html') and 
                ('yapay-zeka' in href or 'ai' in href.lower() or 'chatgpt' in href.lower() or 'gemini' in href.lower()) and
                link.get_text(strip=True) and
                len(link.get_text(strip=True)) > 10):
                news_links.append(link)
        
        print(f"🔍 WebTekno: {len(news_links)} potansiyel haber bulundu")
        
        for article in news_links[:10]:  # İlk 10 haberi kontrol et
            try:
                title = article.get_text(strip=True)
                link = article.get('href')
                
                if not title or not link:
                    continue
                
                # REKLAM/TANITIM FİLTRELERI - WebTekno için
                reklam_kelimeleri = [
                    'reklam', 'sponsor', 'tanıtım', 'duyuru', 'haber bülteni',
                    'newsletter', 'abonelik', 'üyelik', 'kayıt', 'webtekno uygulaması',
                    'uygulamızı indirin', 'mobil uygulama', 'app store', 'google play'
                ]
                
                title_lower = title.lower()
                if any(kelime in title_lower for kelime in reklam_kelimeleri):
                    print(f"🚫 Reklam/tanıtım atlandı: {title[:50]}...")
                    continue
                
                # Tam URL oluştur
                if link.startswith('/'):
                    link = 'https://www.webtekno.com' + link
                elif not link.startswith('http'):
                    link = 'https://www.webtekno.com/' + link
                
                # Resim bul (parent elementlerde ara)
                image_url = None
                parent_elem = article.parent
                for _ in range(3):  # 3 seviye yukarı çık
                    if parent_elem:
                        img_elem = parent_elem.find('img')
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                            if image_url and image_url.startswith('/'):
                                image_url = 'https://www.webtekno.com' + image_url
                            break
                        parent_elem = parent_elem.parent
                    else:
                        break
                
                # Özet yoksa başlığı kısalt
                summary = title[:200] if len(title) > 200 else ""
                
                # Hash oluştur (benzersizlik için)
                content_hash = hashlib.md5((title + link).encode()).hexdigest()
                
                news_items.append({
                    'title': f"[WebTekno] {title}",
                    'url': link,
                    'summary': summary,
                    'image_url': image_url,
                    'content_hash': content_hash,
                    'publish_date': dt.datetime.now().isoformat(),
                    'source': 'WebTekno'
                })
                
                print(f"✅ WebTekno: {title[:50]}...")
                
            except Exception as e:
                print(f"❌ WebTekno haber işleme hatası: {e}")
                continue
        
        return news_items
        
    except Exception as e:
        print(f"❌ WebTekno site çekme hatası: {e}")
        return []

def save_news(news_items):
    """Yeni haberleri veritabanına kaydet"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    new_news = []
    
    for news in news_items:
        try:
            # Daha önce kaydedilmiş mi kontrol et
            existing = conn.execute(
                "SELECT id FROM ai_news WHERE content_hash = ? OR url = ?",
                (news['content_hash'], news['url'])
            ).fetchone()
            
            if not existing:
                # Yeni haber, kaydet
                conn.execute("""
                    INSERT INTO ai_news (title, url, summary, image_url, publish_date, content_hash, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    news['title'],
                    news['url'],
                    news['summary'],
                    news['image_url'],
                    news['publish_date'],
                    news['content_hash'],
                    news.get('source', 'Unknown'),
                    dt.datetime.now().isoformat()
                ))
                new_news.append(news)
                print(f"💾 Yeni haber kaydedildi: {news['title'][:50]}...")
            else:
                print(f"📰 Mevcut haber: {news['title'][:50]}...")
                
        except Exception as e:
            print(f"❌ Kayıt hatası: {e}")
    
    conn.commit()
    conn.close()
    return new_news

def get_unsent_news():
    """Telegram'a gönderilmemiş haberleri getir"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.execute("""
        SELECT id, title, url, summary, image_url, publish_date, source 
        FROM ai_news 
        WHERE sent_to_telegram = 0 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    news = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'summary': row[3],
            'image_url': row[4],
            'publish_date': row[5],
            'source': row[6] if len(row) > 6 else 'Unknown'
        }
        for row in news
    ]

def get_all_news_today():
    """Bugün eklenen tüm haberleri getir (hem gönderilmiş hem gönderilmemiş)"""
    from datetime import datetime, date
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    today = date.today().strftime('%Y-%m-%d')
    
    cursor = conn.execute("""
        SELECT id, title, url, summary, source 
        FROM ai_news 
        WHERE date(created_at) = ? 
        ORDER BY created_at DESC
    """, (today,))
    
    news = cursor.fetchall()
    conn.close()
    
    return news

def mark_as_sent(news_id):
    """Haberi gönderildi olarak işaretle"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("UPDATE ai_news SET sent_to_telegram = 1 WHERE id = ?", (news_id,))
    conn.commit()
    conn.close()

def format_news_message(news):
    """Haber mesajını formatla"""
    message = f"🤖 **Yapay Zeka Haberi**\n\n"
    message += f"📰 **{news['title']}**\n\n"
    
    if news['summary']:
        message += f"📝 {news['summary']}\n\n"
    
    message += f"🔗 [Haberi Oku]({news['url']})\n"
    message += f"📅 {news['publish_date'][:16]}\n"
    message += f"🏷️ #YapayZeka #DonanımHaber"
    
    return message

async def send_news_to_telegram(bot, chat_id, news):
    """Haberi Telegram'a gönder"""
    try:
        message = format_news_message(news)
        
        # Eğer resim varsa, resimle birlikte gönder
        if news['image_url']:
            try:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=news['image_url'],
                    caption=message,
                    parse_mode='Markdown'
                )
            except:
                # Resim gönderilmediyse sadece metin gönder
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram gönderim hatası: {e}")
        return False

def check_and_send_news():
    """Ana kontrol fonksiyonu"""
    print("🔍 Yapay zeka haberleri kontrol ediliyor...")
    print("📡 Kaynak: Donanım Haber + WebTekno")
    
    # Haberleri çek
    news_items = fetch_ai_news()
    
    if not news_items:
        print("❌ Hiç haber bulunamadı")
        return []
    
    # Yeni haberleri kaydet
    new_news = save_news(news_items)
    
    if new_news:
        print(f"🆕 {len(new_news)} yeni haber bulundu!")
        # Kaynak dağılımını göster
        sources = {}
        for news in new_news:
            source = news.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        for source, count in sources.items():
            print(f"   📰 {source}: {count} haber")
        
        return new_news
    else:
        print("📰 Yeni haber yok")
        return []

# Test fonksiyonu
if __name__ == "__main__":
    init_news_db()
    print("🧪 Haber sistemi test ediliyor...")
    
    news = check_and_send_news()
    
    if news:
        print("\n📰 Yeni haberler:")
        for item in news:
            print(f"  - {item['title'][:60]}...")
            print(f"    URL: {item['url']}")
            if item['image_url']:
                print(f"    Resim: {item['image_url']}")
            print()
    else:
        print("📭 Yeni haber yok")
