# -*- coding: utf-8 -*-
from functions import *
from db_helper import *
import helper
import json

async def keyboarding(call: types.CallbackQuery):
    try:
        await call.answer()
    except:
        pass
    user = await User.get(call.from_user.id)
    await User.update(user.tg_id, step=10)
    kb = types.InlineKeyboardMarkup()
    text_storage = eval(user.text_storage)

    if call.data == 'menu':

        text = '''<b>🤓Чат-бот студии массажа лица Oval в Санкт-Петербурге.

В этом боте вы можете:</b>
🔹записаться к нам в студию
🔹посмотреть свои будущие записи
🔹перенести запись на другую дату и время
🔹отменить запись
🔹оплатить визит
🔹купить абонементы и сертификаты
🔹связаться с нами удобным для вас методом из раздела “Контакты”'''

        kb.row_width = 1
        kb.add(types.InlineKeyboardButton('📱Записаться онлайн', callback_data=f'recordMenu'),
               types.InlineKeyboardButton('🙋‍♀️Записаться через администратора', callback_data=f'admin'),
               types.InlineKeyboardButton('📒Контакты', callback_data=f'contacts'),
               types.InlineKeyboardButton('Мои записи', callback_data=f'recordAccount0'))

    elif call.data == 'admin':
        text = 'Вы можете позвонить нам 📲+7 (812) 383 3808, или написать в чат @ovalface. 🕖Время работы с 09:00 до 22:00.'
        kb.row_width = 1
        kb.add(types.InlineKeyboardButton('✍Написать в чат', url='https://t.me/ovalface'),
               types.InlineKeyboardButton('📱Записаться онлайн', callback_data=f'recordMenu'),
               types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

    elif call.data == 'contacts':
        text = '''<b>Студия массажа лица Oval в Санкт-Петербурге🤗</b> 

<b>Связаться с нами</b>:
+7 (812) 383 3808
Онлайн чат с администратором @ovalface
'''
        kb.row_width = 1
        kb.add(types.InlineKeyboardButton('📍Коломяжский 15к1', url='https://yandex.ru/maps/-/CCUmM0Ud-D'),
               types.InlineKeyboardButton('📍Наб. Матисова канала 1', url='https://yandex.ru/maps/org/studiya_massazha_litsa_oval/186515153941/?ll=30.315635%2C59.938951&z=11'),
               types.InlineKeyboardButton('Наш сайт', url='https://ovalface.ru/'),
               types.InlineKeyboardButton('Instagram', url='https://www.instagram.com/face_oval/'),
               types.InlineKeyboardButton('VK', url='https://vk.com/ovalface'),
               types.InlineKeyboardButton('🎀Меню', callback_data=f'menu')
               )
        await bot.send_contact(user.tg_id, '78123833808', first_name='Oval', reply_markup=kb)
        kb = types.InlineKeyboardMarkup()

    elif call.data.startswith('record'):
        call.data = call.data.replace('record', '')

        if call.data == 'Menu':

            text, kb = await menu(text_storage, kb)

        elif call.data.startswith('Address'):
            kb.row_width = 1
            text = 'Выберите адрес:\n'
            for id in json.loads(os.environ.get('ADDRESSES')):
                temp = await y.get_company(id)
                text += f"{temp[0]} по адресу: {temp[1]}\n"
                kb.add(types.InlineKeyboardButton(temp[1], callback_data=f'selectAddress{id}'))
            kb.add(types.InlineKeyboardButton('Вернуться к записи', callback_data=f'recordMenu'),
                   types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Category'):
            page = int(call.data.replace('Category', ''))
            text = f'Выберите интересующую вас категорию: \n'
            categories = await y.get_services(text_storage.get('company_id'))
            for category in categories[page*5:page*5+5]:
                kb.add(types.InlineKeyboardButton(category[1], callback_data=f'recordServices0_{category[0]}'))
            btn_list = []
            if page != 0:
                btn_list.append(
                    types.InlineKeyboardButton('Предыдущая страница', callback_data=f'recordCategory{page - 1}'))
            if len(categories) >= page * 5 + 6:
                btn_list.append(types.InlineKeyboardButton('Следующая страница', callback_data=f'recordCategory{page + 1}'))
            kb.add(*btn_list)

            kb.add(types.InlineKeyboardButton('Вернуться к записи', callback_data=f'recordMenu'))
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Services'):
            call.data = call.data.replace('Services', '').split('_')
            page = int(call.data[0])
            category_id = int(call.data[1])
            service_ids = text_storage.get('service_ids') or {}
            services = await y.get_services(text_storage.get('company_id'), category_id=category_id)

            if len(call.data) > 2:
                service_id = int(call.data[2])
                if service_id in service_ids.keys():
                    service_ids.pop(service_id)
                else:
                    for service in services:
                        if service[0] == service_id:
                            service_ids.update({service_id: service[1]})
                            break

                text_storage.update({'service_ids': service_ids})
                await User.update(user.tg_id, text_storage=str(text_storage))

            text = 'Выберите интересующие вас услуги: \n'
            for service in services[page*5:page*5+5]:
                text += f'{service[1]} - {service[2]}р\n'
                kb.add(types.InlineKeyboardButton(f'{"✅" if service[0] in service_ids else ""}{service[1]} - {service[2]}р',
                                                  callback_data=f'recordServices{page}_{category_id}_{service[0]}'))
            btn_list = []
            if page != 0:
                btn_list.append(
                    types.InlineKeyboardButton('Предыдущая страница', callback_data=f'recordServices{page - 1}_{category_id}'))
            if len(services) >= page * 5 + 6:
                btn_list.append(types.InlineKeyboardButton('Следующая страница', callback_data=f'recordServices{page + 1}_{category_id}'))
            kb.add(*btn_list)

            kb.add(types.InlineKeyboardButton('Вернуться к категориям', callback_data=f'recordCategory0'))
            kb.add(types.InlineKeyboardButton('Закончить выбор услуг', callback_data=f'recordMenu'))
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Worker'):
            page = int(call.data.replace('Worker', ''))
            date = text_storage.get('date', None)
            workers = await y.get_staff(text_storage.get('company_id'), date)
            text = '🤗Выберите мастера: '
            for worker in workers[page*5:page*5+5]:
                kb.add(types.InlineKeyboardButton(f'{worker[1]} {worker[2]}', callback_data=f'selectWorker{worker[0]}'))
            btn_list = []
            if page != 0:
                btn_list.append(
                    types.InlineKeyboardButton('Предыдущая страница', callback_data=f'recordWorker{page - 1}'))
            if len(workers) >= page * 5 + 6:
                btn_list.append(types.InlineKeyboardButton('Следующая страница', callback_data=f'recordWorker{page + 1}'))
            kb.add(*btn_list)

            kb.add(types.InlineKeyboardButton('Вернуться к записи', callback_data=f'recordMenu'))
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Date'):
            call.data = call.data.replace('Date', '')
            page = int(call.data.split('_')[0])

            company_id = text_storage.get('company_id')
            service_ids = text_storage.get('service_ids')
            if service_ids:
                service_ids = [*service_ids.keys()]
            staff = text_storage.get('staff')
            staff_id = 0
            if staff:
                staff_id = staff[0]


            change_param = ''
            record_id = ''
            if len(call.data.split('_')) > 1 and call.data.split('_')[1]:
                change_param = 'New'
                record_id = int(call.data.split('_')[1])
                record = await Record.get(record_id)
                company_id = record.company_id
                service_ids = eval(record.service_ids)
                staff_id = record.master_id

            text = 'Выберите интересующую вас дату, учтите, она может зависеть от выбранных услуг и выбранного мастера'


            dates = await y.get_dates(company_id, service_ids, staff_id)
            
            for date in dates[page*5:page*5+5]:
                temp = date.split('-')
                temp.reverse()
                formatted_date = '.'.join([x for x in temp[:2]])
                kb.add(types.InlineKeyboardButton(f'{formatted_date}', callback_data=f'select{change_param}Date{date}_{record_id}'))
            btn_list = []
            if page != 0:
                btn_list.append(
                    types.InlineKeyboardButton('Предыдущая страница',
                                               callback_data=f'recordDate{page - 1}_{record_id}'))
            if len(dates) >= page * 5 + 6:
                btn_list.append(types.InlineKeyboardButton('Следующая страница',
                                                           callback_data=f'recordDate{page + 1}_{record_id}'))
            kb.add(*btn_list)

            kb.add(types.InlineKeyboardButton('Вернуться к записи', callback_data=f'recordMenu'))
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Time'):
            call.data = call.data.replace('Time', '')
            page = int(call.data.split('_')[0])
            text = 'Выберите интересующее вас время'
            company_id = text_storage.get('company_id')
            staff = text_storage.get('staff')
            staff_id = 0
            if staff:
                staff_id = staff[0]
            service_ids = text_storage.get('service_ids')
            if service_ids:
                service_ids = [*service_ids.keys()]

            change_param = ''
            record_id = ''
            if len(call.data.split('_')) > 1 and call.data.split('_')[1]:
                change_param = 'New'
                record_id = int(call.data.split('_')[1])
                record = await Record.get(record_id)
                company_id = record.company_id
                service_ids = eval(record.service_ids)
                staff_id = record.master_id

            if not change_param:
                text += ', учтите, она может зависеть от выбранных услуг и выбранного мастера'

            date = text_storage.get('new_date') if change_param else text_storage.get('date')

            times = await y.get_times(company_id, staff_id, date, service_ids)

            for time in times[page * 5:page * 5 + 5]:
                kb.add(types.InlineKeyboardButton(f'{time}', callback_data=f'select{change_param}Time{time}_{record_id}'))
            btn_list = []
            if page != 0:
                btn_list.append(
                    types.InlineKeyboardButton('Предыдущая страница',
                                               callback_data=f'recordTime{page - 1}_{record_id}'))
            if len(times) >= page * 5 + 6:
                btn_list.append(types.InlineKeyboardButton('Следующая страница',
                                                           callback_data=f'recordTime{page + 1}_{record_id}'))
            kb.add(*btn_list)

            kb.add(types.InlineKeyboardButton('Вернуться к записи', callback_data=f'recordMenu'))
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Reset'):
            text_storage.update({'company_id': None, 'address': None, 'service_ids': None, 'date': None, 'staff': None,
                                 'time': None})
            await User.update(user.tg_id, text_storage=str(text_storage))
            text, kb = await menu(text_storage, kb)


        elif call.data == 'Accept':

            datetime = f'{text_storage.get("date")}T{text_storage.get("time")}:00+04:00'
            args = [text_storage.get('company_id'), [*text_storage.get('service_ids').keys()],
                    datetime]
            staff = text_storage.get('staff', None)
            if staff:
                staff_id = staff[0]
            else:
                staff_id = 0
            resp = await y.validate_record(*args, staff_id)
            kb.row_width = 1
            if resp:
                text = 'Данное время доступно для записи, вы уверены, что хотите записаться?'
                kb.add(types.InlineKeyboardButton('Да', callback_data='recordCreate'))
            else:
                text = 'Данная дата или мастер заняты в данное время, попробуйте выбрать другую дату'
            kb.add(types.InlineKeyboardButton('Вернуться к записи', callback_data='recordMenu'),
                   types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))


        elif call.data == 'Create':

            company_id = text_storage.get('company_id')

            if user.phone_number is None:
                text = 'Введите ваш мобильный номер для записи'
                await User.update(user.tg_id, step=1)

            elif user.name is None:
                text = 'Введите ваше имя, по которому наши сотрудники могли бы к вам обращаться'
                await User.update(user.tg_id, step=2)

            elif user.auth_hash is not None: #изменить после
                text = 'Введите код подтверждения, который пришел к вам на телефон'
                await User.update(user.tg_id, step=3)
                await y.send_code(company_id, phone_number=user.phone_number)

            else:
                datetime = f'{text_storage.get("date")}T{text_storage.get("time")}:00+04:00'
                args = [text_storage.get('company_id'), user.phone_number, user.name,
                        [*text_storage.get('service_ids').keys()], datetime]

                staff = text_storage.get('staff')
                staff_id = 0
                if staff:
                    staff_id = staff[0]
                services = '\n'.join([x for x in text_storage.get('service_ids').values()])
                service_ids = [*text_storage.get('service_ids').keys()]
                # print(args, staff)
                record_id, record_hash = await y.create_record(*args, staff_id)
                # from tasks import last_attempt_check, birthday_check
                if record_id and record_hash:
                    await Record.create(user_id=user.id, record_id=record_id, record_hash=record_hash, date=datetime,
                                        services=services, master_id=staff_id, company_id=company_id, service_ids=str(service_ids))
                    record_length = await y.get_record_time(company_id=company_id, service_ids=service_ids)
                    delay = helper.get_delay(text_storage.get('date'), text_storage.get('time'))
                    master_tip_link = await y.get_master_tip_link(company_id, staff_id)
                    google_link, yandex_link = await y.get_links(company_id)

                    helper.complex(user.tg_id, delay, record_length, master_tip_link, google_link, yandex_link)

                    text = 'Запись успешно создана!'
                    text_storage.update(
                        {'company_id': None, 'address': None, 'service_ids': None, 'date': None, 'staff': None,
                         'time': None})
                    await User.update(user.tg_id, text_storage=str(text_storage))
                else:
                    text = 'Произошла ошибка при создании записи, возможно, заказанные услуги и время стало занято, либо ' \
                           'недоступно, попробуйте снова'
                    kb.add(types.InlineKeyboardButton('Вернуться к записи', callback_data='recordMenu'))

            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Account'):
            page = int(call.data.replace('Account', ''))
            text = f"Ваше имя: {user.name or 'не указано'} \n" \
                   f"Ваш номер телефона {user.phone_number or 'не указан'}\n" \
                   f"Аккаунт подтвержден по смс: {'да' if user.auth_hash else 'нет'}"

            if user.auth_hash:
                companies = json.loads(os.environ.get('ADDRESSES'))
                list_ids = await y.get_records_ids(user.client_id, companies)
                records = await Record.get_all(owner_id=user.id, list_ids=list_ids)
                records.reverse()
                for record in records[page * 5:page * 5 + 5]:
                    kb.add(types.InlineKeyboardButton(f'{record.date.replace("+04:00", "").replace("T", " ")}',
                                                      callback_data=f'selectRecord{record.id}'))
                btn_list = []
                if page != 0:
                    btn_list.append(
                        types.InlineKeyboardButton('Предыдущая страница', callback_data=f'recordAccount{page - 1}'))
                if len(records) >= page * 5 + 6:
                    btn_list.append(types.InlineKeyboardButton('Следующая страница', callback_data=f'recordAccount{page + 1}'))
                kb.add(*btn_list)
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

        elif call.data.startswith('Delete'):
            record_id = int(call.data.replace('Delete', ''))
            record = await Record.get(record_id)
            text = 'Запись удалена'
            await y.delete_record(record.record_id, user.auth_hash)
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))

    elif call.data.startswith('select'):
        call.data = call.data.replace('select', '')

        if call.data.startswith('Address'):
            company_id = int(call.data.replace('Address', ''))
            temp = await y.get_company(company_id)
            text_storage.update({'company_id': company_id, 'address': temp[1]})
            await User.update(user.tg_id, text_storage=str(text_storage))
            text, kb = await menu(text_storage, kb)

        elif call.data.startswith('Worker'):
            worker_id = int(call.data.replace('Worker', ''))
            workers = await y.get_staff(text_storage.get('company_id'))
            for worker in workers:
                if worker[0] == worker_id:
                    text_storage.update({'staff': worker})
                    await User.update(user.tg_id, text_storage=str(text_storage))
                    break
            text, kb = await menu(text_storage, kb)

        elif call.data.startswith('NewDate'):
            call.data = call.data.replace('NewDate', '')
            date = call.data.split('_')[0]
            record_id = call.data.split('_')[1]
            text_storage.update({'new_date': date})
            await User.update(user.tg_id, text_storage=str(text_storage))
            text = 'Дата выбрана, теперь выберите время'
            kb.row_width = 1
            kb.add(types.InlineKeyboardButton('Выбрать время', callback_data=f'recordTime0_{record_id}'),
                   types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))


        elif call.data.startswith('NewTime'):
            call.data = call.data.replace('NewTime', '')
            time = call.data.split('_')[0]
            record_id = call.data.split('_')[1]
            record = await Record.get(record_id)
            date = text_storage.get('new_date')
            new_datetime = f'{date}T{time}:00+04:00'
            kb.row_width = 1
            status = await y.edit_record(record.company_id, record.record_id, new_datetime, user.auth_hash)
            if status:
                text = 'Дата успешно изменена'
                await Record.update(record.id, date=new_datetime)
            else:
                text = 'Выбранная вами дата устарела, либо недоступна, попробуйте снова'
                kb.add(types.InlineKeyboardButton('Мои записи', callback_data=f'recordAccount0'))
            kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))


        elif call.data.startswith('Date'):
            date = call.data.replace('Date', '').replace('_', '')
            text_storage.update({'date': date})
            await User.update(user.tg_id, text_storage=str(text_storage))
            text, kb = await menu(text_storage, kb)

        elif call.data.startswith('Time'):
            time = call.data.replace('Time', '').replace('_', '')
            text_storage.update({'time': time})
            await User.update(user.tg_id, text_storage=str(text_storage))
            text, kb = await menu(text_storage, kb)

        elif call.data.startswith('Record'):
            record_id = int(call.data.replace('Record', ''))
            record = await Record.get(record_id)
            text = f'Время записи: {record.date.replace("+04:00", "").replace("T", " ")}\n' \
                   f'Услуги: {record.services}'
            kb.row_width = 1
            kb.add(types.InlineKeyboardButton('Перенести', callback_data=f'recordDate0_{record_id}'),
                   types.InlineKeyboardButton('Отменить запись', callback_data=f'recordDelete{record_id}'),
                   types.InlineKeyboardButton('🎀Меню', callback_data='menu'))



    await edit_message_text(call.message, text, reply_markup=kb)


async def chatting(message: types.Message):
    user = await User.get(message.from_user.id)
    kb = types.InlineKeyboardMarkup()

    if user.step == 1:
        try:
            if len(message.text) == 11:
                number = int(message.text)
            else:
                raise Exception
            text = 'Номер введен\n'
            if user.name is None:
                text = 'Для записи также потребуется ввести имя: '
                await User.update(user.tg_id, phone_number=number, step=2)
                kb.add(types.InlineKeyboardButton('Вернуться к созданию записи', callback_data='recordMenu'))
        except:
            text = 'Вы ввели номер в неверном формате. Примеры правильного формата: 8987327021, 7987327021'
        kb.add(types.InlineKeyboardButton('🎀Меню', callback_data='menu'))

    elif user.step == 2:

        try:
            if len(message.text) > 64:
                raise Exception
            text = 'Имя введено'
            await User.update(user.tg_id, name=message.text, step=10)
            kb.add(types.InlineKeyboardButton('Вернуться к созданию записи', callback_data='recordCreate'))
        except:
            text = 'Превышена длина имени'
        kb.add(types.InlineKeyboardButton('🎀Меню', callback_data='menu'))

    elif user.step == 3:
        try:
            hash, client_id = await y.get_user_hash(message.text, user.phone_number)
            if not hash:
               raise Exception
            await User.update(user.tg_id, step=10, auth_hash=hash, client_id=client_id)
            text = 'Авторизация прошла успешно, Вы можете продолжить создание записи, впредь авторизация не потребуется'
            kb.add(types.InlineKeyboardButton('Создать запись', callback_data='recordCreate'))
        except:
            text = 'Введен неверный код'
        kb.add(types.InlineKeyboardButton('🎀Меню', callback_data='menu'))

    await bot.send_message(message.from_user.id, text, reply_markup=kb, parse_mode='html')


async def contactus(message: types.Message):
    user = await User.get(message.from_user.id)
    if not user:
        await User.create(tg_id=message.from_user.id, text_storage='{}', step=0)
    kb = types.InlineKeyboardMarkup(row_width=1)
    text = '''<b>Студия массажа лица Oval в Санкт-Петербурге🤗</b> 

    <b>Связаться с нами</b>:
    +7 (812) 383 3808
    Онлайн чат с администратором @ovalface
    '''
    kb.row_width = 1
    kb.add(types.InlineKeyboardButton('📍Коломяжский 15к1',
                                      url='https://yandex.ru/maps/-/CCUmM0Ud-D'),
           types.InlineKeyboardButton('📍Наб. Матисова канала 1',
                                      url='https://yandex.ru/maps/org/studiya_massazha_litsa_oval/186515153941/?ll=30.315635%2C59.938951&z=11'),
           types.InlineKeyboardButton('Наш сайт', url='https://ovalface.ru/'),
           types.InlineKeyboardButton('Instagram',
                                      url='https://www.instagram.com/face_oval/'),
           types.InlineKeyboardButton('VK', url='https://vk.com/ovalface'),
           types.InlineKeyboardButton('🎀Меню', callback_data=f'menu')
           )
    await bot.send_contact(user.tg_id, '78123833808', first_name='Oval',
                           reply_markup=kb)
    kb = types.InlineKeyboardMarkup()
    await edit_message_text(message, text, reply_markup=kb)


async def onlinerecord(message: types.Message):
    user = await User.get(message.from_user.id)
    if not user:
        user = await User.create(tg_id=message.from_user.id, text_storage='{}',
                                 step=0)
    kb = types.InlineKeyboardMarkup(row_width=1)
    text, kb = await menu(eval(user.text_storage), kb)

    await edit_message_text(message, text, reply_markup=kb)


async def myrecords(message: types.Message):
    user = await User.get(message.from_user.id)
    if not user:
        await User.create(tg_id=message.from_user.id, text_storage='{}',
                          step=0)
    kb = types.InlineKeyboardMarkup(row_width=1)
    page = 0
    text = f"Ваше имя: {user.name or 'не указано'} \n" \
           f"Ваш номер телефона {user.phone_number or 'не указан'}\n" \
           f"Аккаунт подтвержден по смс: {'да' if user.auth_hash else 'нет'}"

    if not user.auth_hash:
        companies = json.loads(os.environ.get('ADDRESSES'))
        list_ids = await y.get_records_ids(user.client_id, companies)
        records = await Record.get_all(owner_id=user.id, list_ids=list_ids)
        records.reverse()
        for record in records[page * 5:page * 5 + 5]:
            kb.add(types.InlineKeyboardButton(
                f'{record.date.replace("+04:00", "").replace("T", " ")}',
                callback_data=f'selectRecord{record.id}'))
        btn_list = []
        if page != 0:
            btn_list.append(
                types.InlineKeyboardButton('Предыдущая страница',
                                           callback_data=f'recordAccount{page - 1}'))
        if len(records) >= page * 5 + 6:
            btn_list.append(types.InlineKeyboardButton('Следующая страница',
                                                       callback_data=f'recordAccount{page + 1}'))
        kb.add(*btn_list)
    kb.add(types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))
    await edit_message_text(message, text, reply_markup=kb)


async def adminrecord(message: types.Message):
    user = await User.get(message.from_user.id)
    if not user:
        user = await User.create(tg_id=message.from_user.id, text_storage='{}',
                          step=0)

    kb = types.InlineKeyboardMarkup(row_width=1)
    text = 'Вы можете позвонить нам 📲+7 (812) 383 3808, или написать в чат @ovalface. 🕖Время работы с 09:00 до 22:00.'
    kb.row_width = 1
    kb.add(types.InlineKeyboardButton('✍Написать в чат',
                                      url='https://t.me/ovalface'),
           types.InlineKeyboardButton('📱Записаться онлайн',
                                      callback_data=f'recordMenu'),
           types.InlineKeyboardButton('🎀Меню', callback_data=f'menu'))
    await edit_message_text(message, text, reply_markup=kb)


async def registration(message: types.Message):
    user = await User.get(message.from_user.id)
    if not user:
        await User.create(tg_id=message.from_user.id, text_storage='{}', step=0)
    kb = types.InlineKeyboardMarkup(row_width=1)
    text = '''<b>🤓Чат-бот студии массажа лица Oval в Санкт-Петербурге.

В этом боте вы можете:</b>
🔹записаться к нам в студию
🔹посмотреть свои будущие записи
🔹перенести запись на другую дату и время
🔹отменить запись
🔹оплатить визит
🔹купить абонементы и сертификаты
🔹связаться с нами удобным для вас методом из раздела “Контакты”'''

    kb.row_width = 1
    kb.add(types.InlineKeyboardButton('📱Записаться онлайн', callback_data=f'recordMenu'),
           types.InlineKeyboardButton('🙋‍♀️Записаться через администратора', callback_data=f'admin'),
           types.InlineKeyboardButton('📒Контакты', callback_data=f'contacts'),
           types.InlineKeyboardButton('Мои записи', callback_data=f'recordAccount0'))

    await bot.send_message(message.from_user.id, text, reply_markup=kb)
