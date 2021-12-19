import json
import os
from datetime import datetime, timezone

from celery import Celery
from celery.schedules import crontab
from telebot import TeleBot

from app.models import User, Record
from functions import y
from app import create_app

celery_backend = 'redis://127.0.0.1:6379/0'
app = Celery('tasks', backend=celery_backend, broker=celery_backend)
app.conf.update(
    timezone='Europe/Moscow'
)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*'), last_attempt_check.s()
    )
    sender.add_periodic_task(
        crontab(minute='*'), birthday_check.s()
    )


@app.task
def send_message(text, tg_id):
    bot = TeleBot(os.getenv("TG_TOKEN"), parse_mode='html')
    bot.send_message(tg_id, text=text)


@app.task
def last_attempt_check():
    text = """Добрый день, давненько Вы не были в нашей студии"""
    appl = create_app()
    print('lac')
    with appl.app_context():
        users = User.query.all()
        now = datetime.now().date()
        print('lac1')
        for user in users:
            if user.tg_id and user.name:
                last_record = Record.query.filter_by(user_id=user.id).order_by(Record.date.desc()).first()
                last_record_date=datetime.fromisoformat(last_record.date).date()
                if (now - last_record_date).days >= 17:
                    send_message.delay(text, user.tg_id)


@app.task
def birthday_check():
    text = """Студия Oval поздравляет Вас с Днем Рождения и желает всего наилучшего"""
    print('bc')
    company_ids = json.loads(os.environ.get('ADDRESSES'))
    for company in company_ids:
        users = y.get_birthday_clients(company)
        print(users)
        if users:
            for user in users:
                tg_id = get_tg_id(user)
                if tg_id:
                    bot = TeleBot(os.getenv("TG_TOKEN"), parse_mode='html')
                    bot.send_message(tg_id, text=text)
                else:
                    print('no match with db')

def get_tg_id(user: dict):
    appl = create_app()
    with appl.app_context():
        user_name = user.get('name')
        user_phone = user.get('phone')
        db_user = User.query.filter(User.name == user_name).filter(User.phone_number.contains(user_phone[5:])).first()
        return db_user.tg_id if db_user else None
