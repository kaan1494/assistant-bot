import os
import asyncio
from telegram import Bot

from news_tracker import init_news_db, check_and_send_news, send_news_to_telegram, mark_as_sent


async def run_once():
    token = os.getenv("TG_TOKEN")
    owner_id = os.getenv("OWNER_ID")

    if not token or not owner_id:
        raise RuntimeError("TG_TOKEN ve OWNER_ID ortam değişkenleri zorunludur.")

    chat_id = int(owner_id)
    init_news_db()

    new_news = check_and_send_news()
    if not new_news:
        print("📰 Yeni haber yok, cron görevi bitti.")
        return

    bot = Bot(token=token)
    sent_count = 0

    for news in new_news:
        success = await send_news_to_telegram(bot, chat_id, news)
        if success:
            news_id = news.get("id")
            if news_id:
                mark_as_sent(news_id)
            sent_count += 1

    print(f"✅ Cron görevinde {sent_count}/{len(new_news)} haber gönderildi.")


if __name__ == "__main__":
    asyncio.run(run_once())
