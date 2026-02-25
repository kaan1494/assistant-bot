"""
Fallback smart assistant helpers.
"""


smart_assistant = object()


async def handle_smart_message(update, ctx, message=""):
    text = (message or "").strip()
    return "Size nasıl yardımcı olabilirim?" if text else "Mesajınızı yazın, yardımcı olayım."


async def handle_availability_check(update, ctx):
    return "Müsaitlik kontrolü için tarih/saat yazabilirsiniz."


async def handle_learn_info(update, ctx, info=""):
    return "Bilgi kaydedildi."


async def show_user_profile(update, ctx):
    return "Profil bilgisi şu anda sınırlı modda çalışıyor."
