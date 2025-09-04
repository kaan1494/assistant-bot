import sqlite3

# Veritabanına bağlan
db = sqlite3.connect('data/assistant.db')
cursor = db.cursor()

# Tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("📋 SQLite Veritabanı: data/assistant.db")
print("="*50)
print("📊 Tablolar:")
for table in tables:
    print(f"  - {table[0]}")

print()

# Her tablonun kayıt sayısını göster
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"📈 {table[0]}: {count} kayıt")

print()

# ai_news tablosundan örnek kayıtları göster
if 'ai_news' in [t[0] for t in tables]:
    print("📰 Son 5 haber:")
    cursor.execute("SELECT source, title, url FROM ai_news ORDER BY id DESC LIMIT 5")
    news = cursor.fetchall()
    for i, (source, title, url) in enumerate(news, 1):
        print(f"  {i}. [{source}] {title[:60]}...")

print()

# reminders tablosunu kontrol et
if 'reminders' in [t[0] for t in tables]:
    cursor.execute("SELECT COUNT(*) FROM reminders")
    reminder_count = cursor.fetchone()[0]
    print(f"⏰ Aktif hatırlatmalar: {reminder_count}")

db.close()
