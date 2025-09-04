"""
Güvenlik ve yetkilendirme sistemi
- Şifre koruması
- Kullanıcı yetkilendirme  
- Giriş kontrolü
"""
import os
from telegram import Update
from telegram.ext import ContextTypes

# Bot şifresi
BOT_PASSWORD = os.getenv("BOT_PASSWORD", "gizli123")
OWNER_ID = os.getenv("OWNER_ID")

# Yetkili kullanıcı listesi
authorized_users = set()

print(f"🔐 Güvenlik sistemi yüklendi!")
print(f"🔑 Bot şifresi: {BOT_PASSWORD}")
if OWNER_ID:
    print(f"👤 Ana kullanıcı ID: {OWNER_ID}")
else:
    print("⚠️ OWNER_ID ayarlanmamış!")

def is_authorized(user_id: str) -> bool:
    """Kullanıcının yetkili olup olmadığını kontrol et"""
    return (OWNER_ID and str(user_id) == str(OWNER_ID)) or user_id in authorized_users

def authorize_user(user_id: str, username: str = "Kullanıcı"):
    """Kullanıcıyı yetkilendir"""
    authorized_users.add(str(user_id))
    print(f"✅ Yeni kullanıcı yetkili: {username} (ID: {user_id})")

def check_password(password: str) -> bool:
    """Şifre doğruluğunu kontrol et"""
    return password == BOT_PASSWORD

def only_authorized(func):
    """Sadece yetkili kullanıcıların erişebileceği fonksiyonlar için decorator"""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        
        if is_authorized(user_id):
            return await func(update, ctx)
        
        # Yetkisiz kullanıcı
        username = update.effective_user.first_name or "Kullanıcı"
        await update.message.reply_text(
            f"🔐 Merhaba {username}!\n"
            f"Bu bot güvenlik koruması altındadır.\n\n"
            f"Erişim için şifreyi girin:\n"
            f"Komut: /sifre ŞIFRE_BURAYA"
        )
        return None
    return wrapper

def basic_auth_check(func):
    """Basit yetki kontrolü (uyarı mesajı ile)"""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        
        if is_authorized(user_id):
            return await func(update, ctx)
        
        await update.message.reply_text("❌ Bu bot özel korumalıdır. Şifreyi girin: /sifre ŞIFRE")
        return None
    return wrapper

async def handle_login(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Şifre giriş fonksiyonu"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.first_name or "Kullanıcı"
    
    # Zaten yetkili mi?
    if is_authorized(user_id):
        return await update.message.reply_text("✅ Zaten giriş yapmışsın!")
    
    # Şifre kontrolü
    if not ctx.args:
        return await update.message.reply_text(
            "🔐 Şifre gir:\n/sifre ŞIFREN\n\n"
            "💡 İpucu: BOT_PASSWORD değişkenini .env dosyasında ayarlayabilirsin"
        )
    
    entered_password = " ".join(ctx.args)
    
    if check_password(entered_password):
        authorize_user(user_id, username)
        await update.message.reply_text(
            f"🎉 Hoş geldin {username}!\n"
            f"✅ Başarıyla giriş yaptın.\n\n"
            f"Artık tüm komutları kullanabilirsin. /start ile başla!"
        )
    else:
        await update.message.reply_text(
            f"❌ Yanlış şifre!\n"
            f"🔐 Tekrar dene: /sifre DOĞRU_ŞİFRE"
        )
        print(f"❌ Başarısız giriş denemesi: {username} (ID: {user_id})")

def get_authorized_count():
    """Yetkili kullanıcı sayısı"""
    base_count = 1 if OWNER_ID else 0
    return base_count + len(authorized_users)
