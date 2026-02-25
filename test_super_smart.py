"""Test super smart engine"""

from super_smart_engine import SuperSmartEngine

print("🧠 SÜPER ZEKİ MOTOR TEST!")
print("=" * 50)

engine = SuperSmartEngine()

# Test 1: Tarih çözücü
print('\n📅 Test 1: Akıllı Tarih Çözücü')
test_messages = [
    "2 gün sonra müsait miyim",
    "ayın 15'inde toplantım var", 
    "05.09.2025 tarihinde müsaitliyim kontrol et",
    "yarın müsait miyim"
]

for msg in test_messages:
    date = engine.smart_date_parser(msg)
    print(f"📨 '{msg}' → 📅 {date}")

print('\n✅ Süper zeki motor çalışıyor!')
