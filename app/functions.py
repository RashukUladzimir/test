import os

from app.models import User
from telebot import TeleBot, types
from flask import current_app
import time

def send_post(text, photo=None):
    bot = TeleBot(current_app.config.get('TG_TOKEN'), parse_mode='html')
    users = User.query.all()
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))
    for i in range(len(users)):
        if i != 0 and i % 25 == 0:
            time.sleep(1)
        if photo:
            bot.send_photo(users[i].tg_id, open(f'{photo}', 'rb'), caption=text, reply_markup=kb)
        else:
            bot.send_message(users[i].tg_id, text=text, reply_markup=kb)
    if photo:
        os.remove(photo)