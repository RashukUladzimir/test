from aiogram import Bot, Dispatcher
from aiogram import types
from yapi import YclientsAPI

from db_helper import *

bot = Bot(token=os.environ.get('TG_TOKEN'), parse_mode='html')
dp = Dispatcher(bot)
y = YclientsAPI(os.environ.get('Y_TOKEN'), os.environ.get('USER_TOKEN'))


async def edit_message_text(message: types.Message, text, reply_markup):
    try:
        return await message.edit_text(text, reply_markup=reply_markup, parse_mode="html")
    except:
        try:
            await message.delete()
        except:
            pass
        await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="html")


async def menu(text_storage, kb):
    service_date = text_storage.get('date')
    service_time = text_storage.get('time')
    worker = text_storage.get('staff')
    worker = f'{worker[1]} {worker[2]}' if worker else None
    service_ids = text_storage.get('service_ids')
    address = text_storage.get('address')
    services = '\n'.join([x for x in service_ids.values()]) if service_ids else None
    text = f'<b>Данные записи:</b>\n' \
           f'📍<b>Адрес салона</b>: {address or "не установлен"}\n' \
           f'🙌<b>Услуги</b>: {services or "не установлены"}\n' \
           f'🗓<b>Дата записи</b>: {service_date or "не установлена"}\n' \
           f'🕖<b>Время записи</b>: {service_time or "не установлено"}\n' \
           f'😇<b>Мастер</b>: {worker or "не установлено"}'
    kb.row_width = 1
    kb.add(types.InlineKeyboardButton(f'{"✅" if address else ""}Выбрать адрес салона', callback_data='recordAddress'))
    if text_storage.get('company_id'):

        kb.add(types.InlineKeyboardButton(f'{"✅" if service_ids else ""}Выбрать услуги', callback_data='recordCategory0'))
        if text_storage.get('service_ids'):
            kb.add(types.InlineKeyboardButton(f'{"✅" if service_date else ""}Выбрать дату', callback_data='recordDate0'),
                   types.InlineKeyboardButton(f'{"✅" if worker else ""}Выбрать мастера (необязательно)', callback_data=f'recordWorker0'),
                   types.InlineKeyboardButton(f'{"✅" if service_time else ""}Выбрать время', callback_data=f'recordTime0'))

            if None not in [service_time, service_date]:
                kb.add(types.InlineKeyboardButton('Подтвердить запись', callback_data=f'recordAccept'))

        kb.add(types.InlineKeyboardButton('Сбросить', callback_data=f'recordReset'))

    kb.add(types.InlineKeyboardButton('🎀Меню', callback_data='menu'))

    return text, kb