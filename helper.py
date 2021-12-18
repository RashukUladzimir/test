from datetime import datetime

import pytz
from celery import chain

from tasks import send_message


def get_delay(date: str, time: str):
    if len(time) == 4:
        time = '0{}'.format(time)
    visit_time = f'{date}T{time}:00+04:00'
    datetime_visit = datetime.fromisoformat(visit_time).replace(tzinfo=pytz.timezone('Europe/Moscow'))
    delay = datetime_visit - datetime.now().replace(tzinfo=pytz.timezone('Europe/Moscow'))
    return int(delay.total_seconds())


def send_invite(user_tg_id, delay):
    text = """Добрый день, не забудьте посетить студию Oval сегодня"""
    if delay != 0:
        send_message.apply_async(args=[text, user_tg_id], countdown=delay)
    else:
        send_message.apply_async(args=[text, user_tg_id], countdown=delay)

def send_tips(user_tg_id, tip_link, delay):
    text = """Добрый день, надеемся, Вам понравилось оказание услуг нашего мастера
    Если хотите, можете оставить ему чаевые, перейдя по этой ссылке: {}""".format(tip_link)
    send_message.apply_async(args=[text, user_tg_id], coundown=delay)


def send_review(user_tg_id, google_link, yandex_link, delay):
    text = """Добрый день, надеемся, Вам понравилось оказание услуг нашей студии.
        Если хотите, можете оставить отзыв, перейдя по этим ссылкам: {} \n {}""".format(
        google_link, yandex_link)
    send_message.apply_async(args=[text, user_tg_id], coundown=delay)


def complex(user_tg_id, delay, record_length, tip_link, google_link, yandex_link):
    text_visit = """Добрый день, не забудьте посетить студию Oval сегодня"""

    text_tip = """Добрый день, надеемся, Вам понравилось оказание услуг нашего мастера
    Если хотите, можете оставить ему чаевые, перейдя по этой ссылке: {}""".format(tip_link)

    text_review = """Добрый день, надеемся, Вам понравилось оказание услуг нашей студии.
        Если хотите, можете оставить отзыв, перейдя по этим ссылкам: {} \n {}""".format(
        google_link, yandex_link)

    rem=0

    if (delay - 7200) < 0:
        visit_countdown = 0
        rem = delay - 7200
    else:
        visit_countdown = delay - 7200

    tip_countdown = 7200 + record_length + rem
    review_countdown = 3000
    chain(
        send_message.si(text_visit, user_tg_id).set(countdown=visit_countdown), #за два часа или сразу если осталось <2 часов
        send_message.si(text_tip, user_tg_id).set(countdown=tip_countdown), # два часа - остаток + время сеанса + 10 минут
        send_message.si(text_review, user_tg_id).set(countdown=review_countdown), # +50 минут с окончания сеанса
    ).apply_async()
