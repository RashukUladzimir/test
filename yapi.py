# -*- coding: utf-8 -*-
import os
import datetime
import aiohttp
import json
import requests

def write_json(data):
    with open('write_jsom.json', 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))

class YclientsAPI():
    def __init__(self, y_token, user_token):
        self.y_token = y_token
        self.user_token = user_token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.yclients.v2+json',
            'Authorization': y_token
        }

    async def get_services(self, company_id, category_id=None):
        url = f'https://api.yclients.com/api/v1/book_services/{company_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                data = (await resp.json())
        data = data['data']

        if category_id:
            services_list = []
            data = data['services']
            for service in data:
                if category_id == service['category_id']:
                    services_list.append([service['id'], service['title'], service['price_max']])
            return services_list

        category_list = []
        data = data['category']
        for category in data:
            category_list.append([category['id'], category['title']])
        return category_list


    async def get_dates(self, company_id, service_ids='', staff_id=''):
        url = f'https://api.yclients.com/api/v1/book_dates/{company_id}'
        if service_ids is None:
            service_ids = ''
        if staff_id is None:
            staff_id = ''
        params = {}
        if service_ids:
            params['service_ids'] = service_ids
        if staff_id:
            params['staff_id'] = staff_id


        # params = {'service_ids': service_ids, 'staff_id': staff_id}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as resp:
                data = (await resp.json())
        print(data)
        if data['success']:
            return data['data']['booking_dates']
        else:
            return []


    async def get_times(self, company_id, staff_id, date, service_ids):
        url = f'https://api.yclients.com/api/v1/book_times/{company_id}/{staff_id or "staff_id"}/{date}'
        params = {'service_ids': service_ids}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as resp:
                data = (await resp.json())
        times_list = []
        for time in data['data']:
            times_list.append(time['time'])
        return times_list


    async def calculate_time(self, staff_id, company_id, service_ids):
        url = f'https://api.yclients.com/api/v1/book_times/{company_id}'
        params = {'service_ids': service_ids}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as resp:
                data = (await resp.json())
        times_list = []
        for time in data['data']:
            times_list.append(time['time'])
        return times_list

    @staticmethod
    def get_name(name: str):
        splitted_name = name.split(' ')
        return splitted_name[0] + ' ' + splitted_name[1]

    async def get_staff(self, company_id, date=None):
        url = f'https://api.yclients.com/api/v1/book_staff/{company_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                data = (await resp.json())
        staff_list = []
        for worker in data['data']:

            if date:
                worker_schedule = await self.get_dates(
                    company_id, staff_id=worker['id']
                )

                if date in worker_schedule:
                    staff_list.append([worker['id'], worker['specialization'], self.get_name(worker['name'])])
            else:
                staff_list.append([worker['id'], worker['specialization'], self.get_name(worker['name'])])

        return staff_list


    async def get_company(self, company_id):
        url = f'https://api.yclients.com/api/v1/company/{company_id}/'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                data = (await resp.json())
        data = data['data']
        return [data['title'], data['address']]


    async def validate_record(self, company_id, services, datetime, staff_id=0):
        url = f'https://api.yclients.com/api/v1/book_check/{company_id}'
        data = {
            "appointments": [
                {
                    "id": staff_id,
                    "services": services,
                    "staff_id": staff_id,
                    "datetime": datetime
                }
            ]
        }
        data = str(data).replace("'", '"')
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, data=data) as resp:
                data = (await resp.json())
        return data['success']


    async def send_code(self, company_id, phone_number, name=''):
        url = f'https://api.yclients.com/api/v1/book_code/{company_id}'
        data = {
            "phone": phone_number,
            "fulname": name
        }
        data = str(data).replace("'", '"')
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, data=data) as resp:
                data = (await resp.json())
        return data['success']


    async def get_user_hash(self, code, phone_number):
        url = 'https://api.yclients.com/api/v1/user/auth'
        data = {
            "phone": phone_number,
            "code": code
        }
        data = str(data).replace("'", '"')
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, data=data) as resp:
                data = (await resp.json())
        if data['success']:
            return data['data']['user_token'], data['data']['id']
        else:
            return None, None


    async def create_record(self, company_id, phone, name, services, datetime, staff_id=0):
        url = f'https://api.yclients.com/api/v1/book_record/{company_id}'
        data = {
            "phone": phone,
            "fullname": name,
            "notify_by_sms": 0,
            "email": '',
            "appointments": [
                {
                    "id": 1,
                    "services": services,
                    "staff_id": staff_id,
                    "datetime": datetime,
                }
            ]
        }
        data = str(data).replace("'", '"')
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, data=data) as resp:
                data = (await resp.json())
        if data['success']:

            url = f'https://api.yclients.com/api/v1/record/{company_id}/{data["data"][0]["record_id"]}'

            extended_headers = self.headers
            extended_headers.update({'Authorization': f'{self.y_token}, {self.user_token}'})
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=extended_headers) as resp:
                    temp = await resp.json()

            record = temp['data']
            record.update({'record_labels': [4455561]}) #изменить позже
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=extended_headers, data=json.dumps(record)) as resp:
                    resp.status

            return data['data'][0]['record_id'], data['data'][0]['record_hash']
        else:
            return None, None

    async def delete_record(self, record_id, auth_token):
        extended_headers = self.headers
        extended_headers.update({'Authorization': f'{self.y_token}, {auth_token}'})
        url = f'https://api.yclients.com/api/v1/user/records/{record_id}/'
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=extended_headers) as resp:

                if resp.status == 204:
                    pass
                else:
                    async with aiohttp.ClientSession() as session:
                        async with session.delete(url, headers=extended_headers) as resp2:
                            return


    async def edit_record(self, company_id, record_id, datetime, auth_token):
        url = f'https://api.yclients.com/api/v1/book_record/{company_id}/{record_id}'
        extended_headers = self.headers
        extended_headers.update({'Authorization': f'{self.y_token}, {auth_token}'})
        data = {
            "datetime": datetime
        }
        data = str(data).replace("'", '"')
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=extended_headers, data=data) as resp:
                data = (await resp.json())
        return data['success']

    async def get_records_ids(self, user_id, companies):
        extended_headers = self.headers
        extended_headers.update({'Authorization': f'{self.y_token}, {self.user_token}'})
        records_ids = []
        for company_id in companies:
            params = {'count': 1000,
                      'start_date': str(datetime.date.today())}
            url = f'https://api.yclients.com/api/v1/records/{company_id}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=extended_headers, params=params) as resp:
                    data = (await resp.json())
            records_ids.extend([x['id'] for x in data['data']])
        return tuple(records_ids)


    async def get_record_time(self, company_id, service_ids):
        extended_headers = self.headers
        extended_headers.update(
            {'Authorization': f'{self.y_token},{self.user_token}'})
        record_length = 0
        for service_id in service_ids:
            url = f'https://api.yclients.com/api/v1/company/{company_id}/services/{service_id}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=extended_headers) as resp:
                    data = (await resp.json())
                record_time = data['data']['duration']
            record_length += record_time
        return record_length


    async def get_master_tip_link(self, company_id, staff_id):
        extended_headers = self.headers
        extended_headers.update(
            {'Authorization': f'{self.y_token},{self.user_token}'})
        url = f'https://api.yclients.com/api/v1/company/{company_id}/staff/{staff_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=extended_headers) as resp:
                data = (await resp.json())
            return data['data']['name'].split(' ')[-1]

    async def get_links(self, company_id):
        url = f'https://api.yclients.com/api/v1/company/{company_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                data = (await resp.json())
                longitude = data['data']['coordinate_lon']
                latitude = data['data']['coordinate_lat']
            google_link = f'https://www.google.com/maps/@{latitude},{longitude}z'
            yandex_link = f'https://yandex.ru/maps/?whatshere[point]={longitude},{latitude}&whatshere[zoom]=17'
            return google_link, yandex_link

    def get_birthday_clients(self, company_id):
        url = f"https://api.yclients.com/api/v1/company/{company_id}/clients/search"
        now = datetime.datetime.now().date()
        extended_headers = self.headers
        extended_headers.update(
            {'Authorization': f'{self.y_token},{self.user_token}'})
        data = {
            "fields": ["name", "id", "phone"],
            "filters": [
                {
                    "type": "birthday",
                    "state": {
                        "from": str(now),
                        "to": str(now)
                    }
                }
            ]
        }
        json_data = json.dumps(data)
        with requests.Session() as s:
            resp = s.post(url, data=json_data, headers=extended_headers)
            return resp.json().get('data')