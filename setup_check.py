#!/usr/bin/env python3
"""
Kurulum Test Scripti - Tüm bağımlılıkları kontrol eder
"""

import sys
import subprocess
import importlib
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def check_python_version():
    """Python sürümünü kontrol et"""
    version = sys.version_info
    print(f"{Colors.BLUE}🐍 Python Sürümü: {version.major}.{version.minor}.{version.micro}{Colors.END}")
    
    if version.major >= 3 and version.minor >= 11:
        print(f"{Colors.GREEN}✅ Python sürümü uygun{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ Python 3.11+ gerekli (Mevcut: {version.major}.{version.minor}){Colors.END}")
        return False

def check_package(package_name, import_name=None):
    """Paket kurulumunu kontrol et"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"{Colors.GREEN}✅ {package_name}{Colors.END}")
        return True
    except ImportError:
        print(f"{Colors.RED}❌ {package_name} - Kurulu değil{Colors.END}")
        return False

def check_all_packages():
    """Tüm paketleri kontrol et"""
    print(f"\n{Colors.BOLD}📦 Paket Kontrolleri:{Colors.END}")
    
    packages = [
        # Temel
        ("telegram", "telegram"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        
        # Ses
        ("gtts", "gtts"),
        ("speechrecognition", "speech_recognition"),
        ("pydub", "pydub"),
        
        # AI/ML
        ("scikit-learn", "sklearn"),
        ("torch", "torch"),
        ("transformers", "transformers"),
        ("matplotlib", "matplotlib"),
        
        # Diğer
        ("dateparser", "dateparser"),
        ("apscheduler", "apscheduler"),
        ("markdownify", "markdownify"),
    ]
    
    installed = 0
    total = len(packages)
    
    for package_name, import_name in packages:
        if check_package(package_name, import_name):
            installed += 1
    
    print(f"\n{Colors.BOLD}📊 Kurulum Durumu: {installed}/{total} paket kurulu{Colors.END}")
    return installed, total

def check_ffmpeg():
    """FFmpeg kurulumunu kontrol et"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ FFmpeg kurulu{Colors.END}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print(f"{Colors.RED}❌ FFmpeg kurulu değil - Ses işleme için gerekli{Colors.END}")
    return False

def check_directories():
    """Gerekli klasörleri kontrol et"""
    print(f"\n{Colors.BOLD}📁 Klasör Kontrolleri:{Colors.END}")
    
    directories = [
        "data",
        "data/models",
        "data/voice", 
        "data/tts",
        "data/docs",
        "data/notes"
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"{Colors.GREEN}✅ {directory}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  {directory} - Oluşturuluyor...{Colors.END}")
            path.mkdir(parents=True, exist_ok=True)
            print(f"{Colors.GREEN}✅ {directory} oluşturuldu{Colors.END}")

def check_database():
    """Veritabanı bağlantısını kontrol et"""
    print(f"\n{Colors.BOLD}🗄️ Veritabanı Kontrolleri:{Colors.END}")
    
    try:
        import sqlite3
        db_path = "data/assistant.db"
        
        # Veritabanı bağlantısı test et
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test tablosu oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                test_data TEXT
            )
        """)
        
        # Test verisi ekle
        cursor.execute("INSERT INTO test_table (test_data) VALUES (?)", ("test",))
        conn.commit()
        
        # Test verisi oku
        cursor.execute("SELECT * FROM test_table WHERE test_data = ?", ("test",))
        result = cursor.fetchone()
        
        if result:
            print(f"{Colors.GREEN}✅ Veritabanı bağlantısı çalışıyor{Colors.END}")
            # Test tablosunu temizle
            cursor.execute("DROP TABLE test_table")
            conn.commit()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Veritabanı hatası: {e}{Colors.END}")
        return False

def run_ai_test():
    """AI özelliklerini test et"""
    print(f"\n{Colors.BOLD}🧠 AI Test:{Colors.END}")
    
    try:
        # Basit AI test
        from deep_learning_fixed import NewsAnalyzer
        
        analyzer = NewsAnalyzer()
        test_result = analyzer.categorize_news("Yapay zeka teknolojisi", "AI test")
        
        if test_result:
            print(f"{Colors.GREEN}✅ AI analiz çalışıyor: {test_result}{Colors.END}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️ AI analiz kısmi çalışıyor{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ AI test hatası: {e}{Colors.END}")
        return False

def generate_install_commands():
    """Eksik paketler için kurulum komutları"""
    print(f"\n{Colors.BOLD}🛠️ Kurulum Komutları:{Colors.END}")
    
    commands = [
        "# Virtual environment oluştur",
        "python -m venv .venv",
        "",
        "# Virtual environment aktive et (Windows)",
        ".venv\\Scripts\\activate",
        "",
        "# Virtual environment aktive et (Linux/Mac)", 
        "source .venv/bin/activate",
        "",
        "# Tüm paketleri kur",
        "pip install -r requirements.txt",
        "",
        "# FFmpeg kur (Windows - Chocolatey)",
        "choco install ffmpeg",
        "",
        "# FFmpeg kur (Ubuntu/Debian)",
        "sudo apt install ffmpeg",
        "",
        "# FFmpeg kur (macOS)", 
        "brew install ffmpeg",
        "",
        "# Türkçe NLP modeli (opsiyonel)",
        "python -m spacy download tr_core_news_sm"
    ]
    
    for cmd in commands:
        if cmd.startswith("#"):
            print(f"{Colors.BLUE}{cmd}{Colors.END}")
        elif cmd == "":
            print()
        else:
            print(f"{Colors.YELLOW}{cmd}{Colors.END}")

def main():
    """Ana test fonksiyonu"""
    print(f"{Colors.BOLD}{Colors.BLUE}🤖 AI Telegram Bot - Kurulum Kontrol Sistemi{Colors.END}")
    print("=" * 60)
    
    # Python sürümü
    python_ok = check_python_version()
    
    # Paket kontrolleri
    installed, total = check_all_packages()
    
    # FFmpeg kontrol
    ffmpeg_ok = check_ffmpeg()
    
    # Klasör kontrolleri
    check_directories()
    
    # Veritabanı kontrol
    db_ok = check_database()
    
    # AI test
    ai_ok = run_ai_test()
    
    # Sonuç
    print(f"\n{Colors.BOLD}📋 KURULUM RAPORU:{Colors.END}")
    print("=" * 40)
    
    success_count = sum([
        python_ok,
        installed == total,
        ffmpeg_ok,
        db_ok,
        ai_ok
    ])
    
    total_checks = 5
    
    if success_count == total_checks:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ TÜM SİSTEMLER HAZIR!{Colors.END}")
        print(f"{Colors.GREEN}🚀 Bot başlatılabilir: python app.py{Colors.END}")
    elif success_count >= 3:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ KISMEN HAZIR ({success_count}/{total_checks}){Colors.END}")
        print(f"{Colors.YELLOW}Bot çalışabilir ama bazı özellikler eksik olabilir{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ KURULUM EKSİK ({success_count}/{total_checks}){Colors.END}")
        print(f"{Colors.RED}Lütfen eksik bileşenleri kurun{Colors.END}")
    
    # Kurulum komutları
    if success_count < total_checks:
        generate_install_commands()

if __name__ == "__main__":
    main()
