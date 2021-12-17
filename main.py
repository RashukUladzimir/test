import asyncio

from functions import bot, dp
from db_helper import database
from bot_routes import keyboarding, registration, chatting, contactus, onlinerecord, myrecords, adminrecord


async def on_startup(dp):
    await database.connect()
    # Регистрация хэндлеров
    dp.register_callback_query_handler(keyboarding)
    dp.register_message_handler(registration, commands=['start'])
    dp.register_message_handler(contactus, commands=['contactus'])
    dp.register_message_handler(onlinerecord, commands=['onlinerecord'])
    dp.register_message_handler(adminrecord, commands=['adminrecord'])
    dp.register_message_handler(myrecords, commands=['myrecords'])
    dp.register_message_handler(chatting, content_types=['text'])

    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    webhook = await bot.get_webhook_info()

    # If URL is bad
    # if webhook.url != WEBHOOK_URL:
    #     # If URL doesnt match current - remove webhook
    #     if not webhook.url:
    #         await bot.delete_webhook()
    #     # Set new URL for webhook
    #     await bot.set_webhook(WEBHOOK_URL)
    if webhook.url:
        await bot.delete_webhook()

    await dp.start_polling()


async def on_shutdown(dp):
    """
    Graceful shutdown. This method is recommended by aiohttp docs.
    """
    # Remove webhook.
    await database.disconnect()
    await bot.delete_webhook()


if __name__ == '__main__':
    asyncio.run(on_startup(dp))
    asyncio.run(on_shutdown(dp))