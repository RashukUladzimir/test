# -*- coding: utf-8 -*-
import databases
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

database = databases.Database(os.environ.get('DB_URL').replace('+pymysql', ''))
y_token = os.environ.get('Y_TOKEN')

class User():

    @staticmethod
    async def update(telegram_id, **kwargs):
        query = "UPDATE user SET "
        for key in kwargs:
            query += f'{key} = :{key}, '
        query = query[:len(query)-2] + ' '
        query += f'WHERE tg_id = {telegram_id}'
        return await database.execute(query=query, values=kwargs)

    @staticmethod
    async def get(telegram_id=None, id=None):
        if telegram_id is not None and id is not None:
            return await database.fetch_one(f"SELECT * FROM user WHERE tg_id={telegram_id} AND id = {id}")
        elif telegram_id is not None:
            return await database.fetch_one(f"SELECT * FROM user WHERE tg_id={telegram_id}")
        elif id is not None:
            return await database.fetch_one(f"SELECT * FROM user WHERE id = {id}")
        else:
            return None

    @staticmethod
    async def create(**kwargs):
        keys = ''
        ace = ''
        for key in kwargs:
            keys += f'{key}, '
            ace +=f':{key}, '
        # values += f"'{kwargs[key]}', "  if isinstance(kwargs[key], str) else f'{kwargs[key]}, '
        keys = keys[:len(keys)-2]
        ace = ace[:len(ace) - 2]
        query = f'INSERT INTO user ({keys}) VALUES ({ace})'
        # print(query)

        return await database.execute(query, values=kwargs)


class Record():

    @staticmethod
    async def update(id, **kwargs):
        query = "UPDATE record SET "
        for key in kwargs:
            query += f'{key} = :{key}, '
        query = query[:len(query)-2] + ' '
        query += f'WHERE id = {id}'
        # print(query)
        return await database.execute(query=query, values=kwargs)

    @staticmethod
    async def get(id=None, owner_id=None):
        if owner_id is not None and id is not None:
            return await database.fetch_one(f"SELECT * FROM record WHERE user_id = {owner_id} AND id = {id}")
        elif owner_id is not None:
            return await database.fetch_one(f"SELECT * FROM record WHERE user_id = {owner_id}")
        elif id is not None:
            return await database.fetch_one(f"SELECT * FROM record WHERE id = {id}")
        else:
            return None

    @staticmethod
    async def create(**kwargs):
        keys = ''
        ace = ''
        for key in kwargs:
            keys += f'{key}, '
            ace +=f':{key}, '
        #     values += f"'{kwargs[key]}', "  if isinstance(kwargs[key], str) else f'{kwargs[key]}, '
        keys = keys[:len(keys)-2]
        ace = ace[:len(ace) - 2]
        query = f'INSERT INTO record ({keys}) VALUES ({ace})'
        # print(query)

        return await database.execute(query, values=kwargs)

    @staticmethod
    async def get_all(owner_id=None, list_ids=None):
        query = f'SELECT * FROM record WHERE user_id = {owner_id}'
        if list_ids is not None:
            if not list_ids:
                list_ids = (-1, -2)
            query += f' AND record_id IN {list_ids}'
        return await database.fetch_all(query)


    @staticmethod
    async def delete(id=None):
        return await database.execute(f'DELETE FROM record WHERE id={id}')

    @staticmethod
    async def get_latest_record(user_id=None):
        return await database.execute(f'SELECT * FROM record WHERE user_id={user_id} ORDER BY id DESC LIMIT 1')