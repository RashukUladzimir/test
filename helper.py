from datetime import datetime

import pytz

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
