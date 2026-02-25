# 🤖 Akıllı Telegram Bot - AI Asistan

Yapay zeka destekli, öğrenen ve hatırlayan Telegram botu. Haber analizi, ses komutları, kişisel asistan özellikleri ve deep learning entegrasyonu ile gelişmiş bir AI sistemi.

## 🚀 Özellikler

### 📰 Haber Sistemi
- **Çift Kaynak Haber Toplama**: Donanım Haber + WebTekno
- **Otomatik Filtreleme**: Reklam ve spam içerik temizleme
- **Zamanlanmış Güncellemeler**: 2 saatte bir otomatik haber çekme
- **AI Analizi**: Kategori sınıflandırma ve duygu analizi

### 🧠 Akıllı Öğrenme Sistemi
- **Kullanıcı Profili Oluşturma**: Adınızı, tercihlerinizi hatırlar
- **Randevu Takibi**: "Yarın toplantım var" gibi ifadeleri anlayıp hatırlar
- **Konuşma Geçmişi**: Önceki sohbetleri analiz ederek bağlam oluşturur
- **Intent Analizi**: Ne istediğinizi anlayıp uygun yanıt verir

### 🎤 Ses İşleme
- **Konuşma Tanıma**: Ses mesajlarını metne çevirir
- **Sesli Yanıt**: Metni sese dönüştürür (Türkçe TTS)
- **Audio Format Desteği**: OGG, WAV, MP3 destekli

### 🔬 AI & Deep Learning
- **Haber Analizi**: Scikit-learn ile kategori sınıflandırma
- **Duygu Analizi**: Haberlerin pozitif/negatif analizi
- **Trend Takibi**: Popüler konuları tespit etme
- **PyTorch Entegrasyonu**: Gelişmiş ML modelleri için hazır

## 📋 Gereksinimler

### Python Sürümü
```
Python 3.11+ (Önerilen: 3.13)
```

### Temel Kütüphaneler
```bash
# Bot Framework
python-telegram-bot[all]==21.0.1

# Web Scraping & HTTP
requests==2.31.0
beautifulsoup4==4.12.2
aiohttp==3.9.1

# Veri İşleme
pandas==2.1.4
numpy==1.24.4
sqlite3  # Python ile birlikte gelir

# Ses İşleme
gtts==2.4.0
speechrecognition==3.10.0
pydub==0.25.1

# Görev Zamanlama
apscheduler==3.10.4

# Tarih İşleme
dateparser==1.2.0

# Metin İşleme
markdownify==0.11.6
```

### AI & Machine Learning
```bash
# Deep Learning
torch==2.8.0+cpu
torchvision==0.18.0+cpu
torchaudio==2.8.0+cpu

# NLP & Transformers
transformers==4.36.2
tokenizers==0.15.0

# Klasik ML
scikit-learn==1.3.2

# Veri Görselleştirme
matplotlib==3.8.2
seaborn==0.13.0

# Doğal Dil İşleme
nltk==3.8.1
spacy==3.7.2

# API Entegrasyonları
wikipedia-api==0.6.0
```

### Sistem Gereksinimleri
```bash
# Audio işleme için (Windows)
ffmpeg  # Ses formatları için gerekli

# Memory: En az 4GB RAM (AI özellikleri için 8GB+ önerili)
# Disk: En az 2GB boş alan (modeller için)
```

## 🛠️ Kurulum

## ⚡ Hızlı Başlangıç (Windows PowerShell)

```powershell
# 1. Virtual environment oluştur ve aktive et
python -m venv .venv
.\.venv\Scripts\activate

# 2. Tüm bağımlılıkları kur
pip install -r requirements.txt

# 3. Türkçe korpus verilerini indir
python download_tr_capped.py

# 4. Botu başlat
python app.py
```

> 💡 **Not**: Bot token'ını `app.py` dosyasında güncellemeyi unutmayın!

## ☁️ Render'da 7/24 Çalıştırma

Bu proje Telegram bot olduğu için Render'da **Web Service** yerine **Background Worker** olarak çalıştırılmalıdır.

### 1) GitHub ile güvenli senkron

Yerelde değişikliklerin olduğu için önce korumaya al:

```powershell
# Değişiklikleri geçici sakla
git stash push -u -m "local-before-render"

# Uzak dalı güncelle
git fetch origin

# Bu proje için ana çalışma dalı
git checkout feature/windows-quickstart

# Uzak dal ile senkron
git pull origin feature/windows-quickstart

# Gerekirse yerel değişiklikleri geri getir
git stash pop
```

### 2) Render Blueprint ile deploy

Bu repoda `render.yaml` ve `requirements-render.txt` hazır.

- Render panelinde **New + -> Blueprint** seç
- GitHub repo'yu bağla
- `render.yaml` otomatik algılanır
- Servis türü: `worker` (7/24 çalışır)

### 3) Render ortam değişkenleri

Render servisinde şu değişkenleri ekle:

- `TG_TOKEN` = Telegram bot token
- `OWNER_ID` = kendi Telegram kullanıcı ID
- `TZ` = `Europe/Istanbul`

### 4) Çalıştırma komutları

- Build: `pip install --upgrade pip && pip install -r requirements-render.txt`
- Start: `python app.py`

### 5) Önemli not

Free plan politikaları değişebildiği için gerçek 7/24 çalışma için Render'da genelde **Starter/paid worker** gerekir.

## 📊 Türkçe Korpus İndirme Sistemi

### Korpus İndiricisi - `download_tr_capped.py`

Hugging Face'ten Türkçe korpusları boyut sınırlı şekilde indiren streaming downloader:

**Desteklenen Kaynaklar:**
- **Wikipedia (20231101.tr)**: 1.2 GB limit - 645,768 makale
- **OSCAR-2301 (tr)**: 2.0 GB limit - CommonCrawl verisi  
- **mC4 (tr)**: 1.6 GB limit - Çokdilli C4 korpusu

**Toplam Hedef**: ~4.8 GB Türkçe korpus

### Çalıştırma

```bash
# Tüm korpusları indir
python download_tr_capped.py

# Sadece belirli kaynağı indir
python download_tr_capped.py --source wikipedia
python download_tr_capped.py --source oscar
python download_tr_capped.py --source mc4

# Bağlantı testi (indirme yapma)
python download_tr_capped.py --dry-run
```

### Boyut Kontrol (Windows PowerShell)

```powershell
gci data\raw\tr_wikipedia\wikipedia_tr.jsonl | select Name,Length
gci data\raw\tr_oscar\oscar_tr.jsonl | select Name,Length
gci data\raw\tr_mc4\mc4_tr.jsonl | select Name,Length
```

### Gerekirse Sıkıştırma

```python
import gzip, shutil, pathlib
for f in ["data/raw/tr_wikipedia/wikipedia_tr.jsonl",
          "data/raw/tr_oscar/oscar_tr.jsonl", 
          "data/raw/tr_mc4/mc4_tr.jsonl"]:
    p = pathlib.Path(f)
    if p.exists() and not p.with_suffix(p.suffix+".gz").exists():
        with open(p,"rb") as fin, gzip.open(str(p)+".gz","wb") as fout:
            shutil.copyfileobj(fin, fout)
print("gzipped")
```

### Veri Yenileme

```bash
# Tools modülü ile korpus güncelleme
python -m tools.fetch_tr_data

# Sadece belirli kaynak
python -m tools.fetch_tr_data --source wikipedia
python -m tools.fetch_tr_data --source oscar
python -m tools.fetch_tr_data --source mc4

# Dosya durumu kontrol
python -m tools.fetch_tr_data --check
```

### Korpus Test Komutları

```bash
# Korpus okuyucu testi
python corpus_reader.py

# AI sistemi korpus entegrasyonu testi (YENİ)
python smart_assistant_korpus.py

# Korpus entegrasyonu ile yanıt testi
python -c "
from smart_assistant_korpus import SmartAssistant
assistant = SmartAssistant()
print('📊 Korpus durumu:')
info = assistant.get_corpus_info()
print(f\"Aktif: {info['available']}\")
if info['available']:
    for src, stats in info['stats'].items():
        if stats['exists']:
            print(f\"  {src}: {stats['size_mb']:.1f} MB\")
print('\n🔍 Test araması:')
response = assistant.search_and_respond(12345, 'teknoloji hakkında')
print(response[:300] + '...' if response and len(response) > 300 else response)
"

# Korpus arama testi
python -c "
from corpus_reader import TurkishCorpusReader
reader = TurkishCorpusReader()
results = reader.search_text('yapay zeka', limit=3)
for r in results:
    print(f\"{r['source']}: {r['text'][:150]}...\")
"
```

### Kabul Kriteri

✅ **Başarılı kurulum kontrolü:**
- [ ] 3 korpus dosyası indirilmiş (Wikipedia, OSCAR, mC4)
- [ ] Toplam boyut 4-6 GB arasında
- [ ] AI sistemi korpusları okuyabiliyor
- [ ] Arama fonksiyonu çalışıyor
- [ ] Bot korpus bilgisiyle yanıt verebiliyor

```powershell
# Hızlı doğrulama
gci data\raw\tr_*\*.jsonl | select Name,Length | ft
python -c "from smart_assistant import SmartAssistant; print('Korpus:', SmartAssistant().get_corpus_info()['available'])"
```

---

### 1. Proje Klonlama
```bash
git clone <repository-url>
cd assistant
```

### 2. Virtual Environment Oluşturma
```bash
# Python virtual environment
python -m venv .venv

# Aktivasyon (Windows)
.venv\Scripts\activate

# Aktivasyon (Linux/Mac)
source .venv/bin/activate
```

### 3. Kütüphane Kurulumu

#### Temel Kurulum
```bash
pip install -r requirements.txt
```

#### Manuel Kurulum
```bash
# Temel bot kütüphaneleri
pip install python-telegram-bot[all] gtts speechrecognition requests beautifulsoup4 apscheduler

# Veri işleme
pip install pandas numpy matplotlib markdownify dateparser

# Ses işleme
pip install pydub

# AI kütüphaneleri
pip install scikit-learn

# Deep Learning (CPU versiyonu)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# NLP kütüphaneleri
pip install transformers tokenizers

# Ek kütüphaneler
pip install wikipedia-api nltk spacy
```

#### GPU Desteği (Opsiyonel)
```bash
# NVIDIA GPU varsa
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. FFmpeg Kurulumu (Ses İşleme)

#### Windows
```bash
# Chocolatey ile
choco install ffmpeg

# Manuel: https://ffmpeg.org/download.html adresinden indirin
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

### 5. Spacy Türkçe Model
```bash
python -m spacy download tr_core_news_sm
```

### 6. Bot Token Yapılandırması
```bash
# .env dosyası oluşturun veya doğrudan app.py'de token'ı güncelleyin
BOT_TOKEN="your_telegram_bot_token_here"
```

## 📚 Türkçe Korpus İndirme (5–6 GB Tavan)

> ⚠️ **Dikkat**: Bu işlem 5-6 GB veri indirecektir. Yeterli disk alanı ve stabil internet bağlantısı olduğundan emin olun.

### Gerekli Paketleri Kurun
```bash
pip install datasets huggingface_hub tqdm
```

### 1. Türkçe Wikipedia Korpusu (≈ 1.5 GB)
```bash
python -c "
from datasets import load_dataset
import os

# Klasörü oluştur
os.makedirs('data/raw/tr_wikipedia', exist_ok=True)

print('📖 Türkçe Wikipedia indiriliyor...')
dataset = load_dataset('wikipedia', '20220301.tr', cache_dir='data/raw/tr_wikipedia')

# JSONL formatında kaydet
with open('data/raw/tr_wikipedia/wikipedia_tr.jsonl', 'w', encoding='utf-8') as f:
    for item in dataset['train']:
        f.write(f'{item}\n')

print('✅ Wikipedia korpusu hazır: data/raw/tr_wikipedia/')
"
```

### 2. Türkçe OSCAR Korpusu (≈ 2.5 GB)
```bash
python -c "
from datasets import load_dataset
import os

# Klasörü oluştur
os.makedirs('data/raw/tr_oscar', exist_ok=True)

print('🌐 Türkçe OSCAR korpusu indiriliyor...')
dataset = load_dataset('oscar-corpus/OSCAR-2301', 'tr', cache_dir='data/raw/tr_oscar')

# İlk 1M satırı al (boyut kontrolü için)
with open('data/raw/tr_oscar/oscar_tr.jsonl', 'w', encoding='utf-8') as f:
    for i, item in enumerate(dataset['train']):
        if i >= 1000000:  # 1M satır limiti
            break
        f.write(f'{item}\n')

print('✅ OSCAR korpusu hazır: data/raw/tr_oscar/')
"
```

### 3. Türkçe mC4 Korpusu (≈ 2 GB)
```bash
python -c "
from datasets import load_dataset
import os

# Klasörü oluştur
os.makedirs('data/raw/tr_mc4', exist_ok=True)

print('📝 Türkçe mC4 korpusu indiriliyor...')
dataset = load_dataset('allenai/c4', 'tr', cache_dir='data/raw/tr_mc4')

# İlk 500K satırı al
with open('data/raw/tr_mc4/mc4_tr.jsonl', 'w', encoding='utf-8') as f:
    for i, item in enumerate(dataset['train']):
        if i >= 500000:  # 500K satır limiti
            break
        f.write(f'{item}\n')

print('✅ mC4 korpusu hazır: data/raw/tr_mc4/')
"
```

### 4. Tüm Korpusları Birleştirme
```bash
python -c "
import json
import os
from tqdm import tqdm

print('🔗 Korpuslar birleştiriliyor...')

# Çıktı dosyası
output_file = 'data/raw/turkish_corpus_combined.jsonl'

# Tüm korpus dosyalarını birleştir
corpus_files = [
    'data/raw/tr_wikipedia/wikipedia_tr.jsonl',
    'data/raw/tr_oscar/oscar_tr.jsonl', 
    'data/raw/tr_mc4/mc4_tr.jsonl'
]

with open(output_file, 'w', encoding='utf-8') as outf:
    for corpus_file in corpus_files:
        if os.path.exists(corpus_file):
            print(f'📄 {corpus_file} ekleniyor...')
            with open(corpus_file, 'r', encoding='utf-8') as inf:
                for line in tqdm(inf):
                    outf.write(line)

print(f'✅ Birleştirilmiş korpus hazır: {output_file}')
print(f'📊 Toplam boyut: {os.path.getsize(output_file) / (1024**3):.2f} GB')
"
```

### 5. Korpus İstatistikleri
```bash
python -c "
import os
import json

# Dosya boyutları
files = {
    'Wikipedia': 'data/raw/tr_wikipedia/wikipedia_tr.jsonl',
    'OSCAR': 'data/raw/tr_oscar/oscar_tr.jsonl',
    'mC4': 'data/raw/tr_mc4/mc4_tr.jsonl',
    'Birleşik': 'data/raw/turkish_corpus_combined.jsonl'
}

print('📊 TÜRKÇE KORPUS İSTATİSTİKLERİ')
print('=' * 50)

total_size = 0
for name, filepath in files.items():
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        size_gb = size / (1024**3)
        total_size += size
        
        # Satır sayısı
        with open(filepath, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        
        print(f'{name:12}: {size_gb:5.2f} GB ({line_count:,} satır)')
    else:
        print(f'{name:12}: ❌ Bulunamadı')

print('-' * 50)
print(f'{'TOPLAM':12}: {total_size / (1024**3):5.2f} GB')
print('✅ Korpus indirme tamamlandı!')
"
```

### 🧹 Temizlik (Opsiyonel)
Sadece birleştirilmiş korpusu kullanacaksanız ayrı dosyaları silebilirsiniz:
```bash
# Windows
rmdir /s data\raw\tr_wikipedia data\raw\tr_oscar data\raw\tr_mc4

# Linux/Mac  
rm -rf data/raw/tr_wikipedia data/raw/tr_oscar data/raw/tr_mc4
```

## 🏗️ Proje Yapısı

```
assistant/
│
├── app.py                 # Ana bot dosyası
├── news_tracker.py        # Haber toplama sistemi
├── smart_assistant.py     # Akıllı öğrenme motoru
├── ai_features.py         # AI analiz komutları
├── deep_learning.py       # Deep learning modülü
├── data_analysis.py       # Veri analiz araçları
│
├── data/                  # Veri klasörü
│   ├── assistant.db       # SQLite veritabanı
│   ├── docs/             # Belgeler
│   ├── notes/            # Notlar
│   ├── tts/              # TTS dosyaları
│   ├── voice/            # Ses dosyaları
│   └── models/           # AI modelleri
│
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Bu dosya
└── bot.log               # Log dosyası
```

## ▶️ Çalıştırma

### Normal Başlatma
```bash
python app.py
```

### Virtual Environment ile
```bash
.venv\Scripts\python.exe app.py  # Windows
.venv/bin/python app.py          # Linux/Mac
```

### Background'da Çalıştırma
```bash
# Windows
start /B python app.py

# Linux/Mac
nohup python app.py &
```

## 🎯 Kullanım

### Bot Komutları

#### Temel Komutlar
```
/start          - Botu başlat
/help           - Yardım menüsü
/haber          - Son haberleri getir
/ses_komut      - Ses komutlarını etkinleştir
```

#### AI Komutları
```
/analiz         - Haber analizi yap
/ozet           - Haber özeti oluştur
/trend          - Trend analizi
/ai             - AI ile sohbet
```

#### Akıllı Asistan
```
/ogren          - Öğrenme sistemini göster
/profil         - Kullanıcı profilini göster
/musait         - Müsaitlik durumunu kontrol et
/not            - Not al
```

#### Ses Komutları
```
🎤 Ses mesajı gönder    - Otomatik konuşma tanıma
"Haber getir"           - Sesli haber talebi
"Analiz yap"            - Sesli analiz komutu
```

### Öğrenme Örnekleri

Bot şu tür ifadeleri anlar ve hatırlar:

```
# Kişisel Bilgiler
"Adım Mehmet"
"Ben İstanbul'da yaşıyorum"
"Yazılım geliştirici olarak çalışıyorum"

# Randevular
"Yarın 14:00'te toplantım var"
"Gelecek hafta doktora gideceğim"
"Pazartesi müsait değilim"

# Tercihler
"Teknoloji haberlerini seviyorum"
"AI konularıyla ilgileniyorum"
"Sabah haberleri okumak isterim"
```

## 🔧 Yapılandırma

### Veritabanı Tabloları
```sql
-- Ana tablolar otomatik oluşturulur
user_profile        # Kullanıcı bilgileri
learned_info        # Öğrenilen bilgiler
conversation_history # Sohbet geçmişi
availability        # Müsaitlik durumu
ai_news            # Haber analiz verileri
reminders          # Hatırlatmalar
notes              # Notlar
```

### Haber Kaynakları
```python
# news_tracker.py içinde konfigüre edilebilir
SOURCES = {
    "donanimhaber": "https://www.donanimhaber.com/",
    "webtekno": "https://www.webtekno.com/"
}
```

### AI Modelleri
```python
# deep_learning.py içinde
MODELS = {
    "sentiment": "basic",           # Basit duygu analizi
    "classification": "sklearn",   # Scikit-learn sınıflandırma
    "nlp": "transformers"         # Hugging Face modelleri
}
```

## 🐛 Sorun Giderme

### Yaygın Hatalar

#### 1. Import Hataları
```bash
# Eksik kütüphane
pip install <missing_package>

# Virtual environment kontrol
which python  # Linux/Mac
where python  # Windows
```

#### 2. Ses İşleme Hataları
```bash
# FFmpeg kurulumu kontrol
ffmpeg -version

# Audio format hataları
pip install pydub[mp3]
```

#### 3. Bot Token Hataları
```python
# app.py içinde token kontrolü
BOT_TOKEN = "your_bot_token_here"  # Doğru format
```

#### 4. Veritabanı Hataları
```bash
# Veritabanı dosyası izinleri
chmod 664 data/assistant.db  # Linux/Mac

# Data klasörü oluşturma
mkdir -p data/models data/voice data/tts
```

### Log Kontrolü
```bash
# Log dosyasını kontrol et
tail -f bot.log

# Debug modu
python app.py --debug
```

## 🔄 Güncelleme

### Kütüphane Güncelleme
```bash
pip list --outdated
pip install --upgrade <package_name>
```

### Bot Güncelleme
```bash
git pull origin main
pip install -r requirements.txt
```

## 📈 Performans

### Bellek Kullanımı
- **Temel Bot**: ~50-100 MB
- **AI Özellikleri**: ~200-500 MB
- **Deep Learning**: ~1-2 GB

### Optimizasyon
```python
# CPU versiyonu için
torch.set_num_threads(2)

# Memory limit
import resource
resource.setrlimit(resource.RLIMIT_AS, (2*1024*1024*1024, -1))  # 2GB limit
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🔗 Bağlantılar

- [Python Telegram Bot](https://python-telegram-bot.org/)
- [PyTorch](https://pytorch.org/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Scikit-learn](https://scikit-learn.org/)

## ⚡ Hızlı Başlangıç

```bash
# 1. Klonla
git clone <repo>
cd assistant

# 2. Sanal ortam oluştur
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Kütüphaneleri kur
pip install python-telegram-bot[all] pandas numpy scikit-learn torch transformers

# 4. Bot token'ı ekle
# app.py içinde BOT_TOKEN değişkenini düzenle

# 5. Çalıştır
python app.py
```

Bot başarıyla çalıştığında şu mesajı göreceksiniz:
```
🚀 Bot başlatılıyor...
🧠 Akıllı öğrenme sistemi aktif!
📰 Haber sistemi hazır - Son güncelleme: [zaman]
🎤 Ses komutları aktif!
✅ Bot hazır! Telegram'dan mesaj gönderebilirsiniz.
```

## 🎯 Sonraki Güncellemeler

- [ ] Çoklu dil desteği
- [ ] Görsel analiz (resim/video)
- [ ] Web arayüzü
- [ ] RESTful API
- [ ] Docker containerization
- [ ] Cloud deployment rehberi
