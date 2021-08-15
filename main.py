from api.search_users import search_users
from api.create_request import create_request
from api.database import BotDB
from random import randrange
import re
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


def check_sex(string):
    return len(string) and (string == 'м' or string == 'ж')


def check_age(string):
    return re.match(r"^\d+$", string) and int(string) > 8


def check_status(string):
    return re.match(r"^[1-8]", string) and len(string) == 1


def check_city(self, string, id, token):
    params = {
        'access_token': token,
        'q': string,
        'country_id': 1,
        'count': 1,
        'v': '5.131'
    }
    result = create_request('database.getCities', params)
    if len(result['response']['items']) > 0:
        city_id = result['response']['items'][0]['id']
        for us in self.USERS:
            if us['id'] == id:
                us['city'] = city_id
        return True
    return False


class Bot:
    def __init__(self):
        self.token = input('Введите токен сообщества...')
        self.token_user = input('Введите токен пользователя...')
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)
        self.USERS = []
        self.question = ''
        self.db = BotDB()
        self.current_user = None
        self.count = 0

    def main(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    user = self.get_user(event.user_id)
                    self.current_user = self.db.get_user(user['id'])
                    if self.current_user:
                        self.create_data(self.current_user, self.token_user)
                    else:
                        self.current_user = None
                        if request == "привет" and self.question == '':
                            self.write_msg(event.user_id, f"Хай, {user['first_name']} {user['last_name']}")
                            self.process_info(user)
                        elif self.question == 'age' and check_age(request):
                            self.add_age(request, event.user_id)
                            self.process_info(user)
                        elif self.question == 'sex' and check_sex(request):
                            self.add_sex(request, event.user_id)
                            self.process_info(user)
                        elif self.question == 'status' and check_status(request):
                            self.add_status(request, event.user_id)
                            self.process_info(user)
                        elif self.question == 'city' and check_city(request, event.user_id, self.token_user):
                            self.process_info(user)
                        else:
                            self.write_msg(event.user_id, "Не поняла вашего ответа...")
                            self.process_info(user)



    def get_sex(self, id):
        self.write_msg(id, 'Введие ваш пол в формате "м" или "Ж"')

    def get_city(self, id):
        self.write_msg(id, 'Введите ваш город')

    def get_age(self, id):
        self.write_msg(id, 'Введите ваш возраст')

    def get_status(self, id):
        self.write_msg(id, """
        Введите ваше семейное положение (пример) \n
        1 - не женат (не замужем),
        2 - встречается,
        3 - помолвлен,
        4 - женат (замужем),
        5 - всё сложно,
        6 - в активном поиске,
        7 - влюблен,
        8 - в гражданском браке
        """)

    def add_user(self, new_user):
        self.USERS.append({
            'id': new_user['id'],
            'sex': new_user['sex'],
            'city': new_user['city']['id'] if 'city' in new_user else '',
            'age': '',
            'status': new_user['status']
        })

    def add_age(self, age, id):
        for us in self.USERS:
            if us['id'] == id:
                us['age'] = age

    def add_sex(self, sex, id):
        sex_code = 1 if sex == 'ж' else 2
        for us in self.USERS:
            if us['id'] == id:
                us['sex'] = sex_code

    def add_status(self, status, id):
        for us in self.USERS:
            if us['id'] == id:
                us['status'] = status

    def check_user(self, id):
        for us in self.USERS:
            if us['id'] == id:
                return True
        return False

    def check_info(self, id):
        for us in self.USERS:
            if us['id'] == id:
                if us['age'] == '':
                    self.question = 'age'
                    self.get_age(id)
                elif us['sex'] == '':
                    self.question = 'sex'
                    self.get_sex(id)
                elif us['city'] == '':
                    self.question = 'city'
                    self.get_city(id)
                elif us['status'] == '':
                    self.question = 'status'
                    self.get_status(id)
                else:
                    self.create_data(us, self.token_user)

    def create_data(self, user, token):
        if self.current_user:
            self.count = len(self.db.get_search_user(user['id']))
        data = search_users(user, token, self.count)
        self.write_msg(user['id'],
                       f'https://vk.com/id{data["id"]}, {data["photos"][0]["url"]}, {data["photos"][1]["url"]}, {data["photos"][2]["url"]}')
        if self.current_user:
            self.db.add_search_user(user, data["id"])
        else:
            self.db.add_search_user(user, data["id"])
            self.db.add_user(user)


    def get_user(self, user_id):
        params = {
            'access_token': token,
            'user_ids': user_id,
            'v': '5.89',
            'fields': 'sex, city, status'
        }
        result = create_request('users.get', params)
        return result['response'][0]

    def process_info(self, user):
        if self.check_user(user['id']):
            self.check_info(user['id'])
        else:
            self.add_user(user)
            self.check_info(user['id'])

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


if __name__ == '__main__':
    bot = Bot()
    bot.main()
