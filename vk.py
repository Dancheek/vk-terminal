import requests
import lxml.html
import re
import json
import os
from getpass import getpass

from appdirs import AppDirs


CONFIG_PATH = os.path.join(AppDirs('Dancheek', 'vk').user_config_dir, 'vk.cfg')


class invalid_password(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class not_valid_method(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class VkSession:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.hashes = {}
        self.cached_users = {}
        self.auth()

    def auth(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Connection':'keep-alive',
            'DNT':'1'}
        self.session = requests.session()
        data = self.session.get('https://vk.com/', headers=headers)
        page = lxml.html.fromstring(data.content)
        form = page.forms[0]
        form.fields['email'] = self.login
        form.fields['pass'] = self.password
        response = self.session.post(form.action, data=form.form_values())
        if "onLoginDone" not in response.text:
            raise invalid_password("Неправильный пароль!")
        return

    def get_api(self):
        return VkApiMethod(self)

    def upload_file(self, filename, prefix='doc', type='doc'):
        vk = self.get_api()
        upload_url = vk.docs.get_messages_upload_server(type=type)['upload_url']

        files = [('file', (filename, open(filename, 'rb')))]
        url2 = requests.post(upload_url, files=files).text

        data = json.loads(url2)
        try:
            response = data['file']
        except KeyError:
            print(f'{data["error"]}: {data["error_descr"]}')
            return ''

        response2 = vk.docs.save(file=response)

        file_id = response2[0]['id']
        file_owner_id = response2[0]['owner_id']

        document = f'{prefix}{file_owner_id}_{file_id}'
        return document

    def upload_image(self, filename):
        vk = self.get_api()
        upload_url = vk.photos.get_messages_upload_server()['upload_url']

        files = [('file', (filename, open(filename, 'rb')))]
        response = requests.post(upload_url, files=files)

        response2 = vk.photos.save_messages_photo(**response.json())

        file_id = response2[0]['id']
        file_owner_id = response2[0]['owner_id']

        document = f'photo{file_owner_id}_{file_id}'
        return document

    def upload_voice(self, filename):
        return self.upload_file(filename, type='audio_message')

    def method(self, method, v=5.87, **params):
        if method not in self.hashes:
            self._get_hash(method)
        data = {'act': 'a_run_method','al': 1,
                'hash': self.hashes[method],
                'method': method,
                'param_v':v}
        for i in params:
            data["param_"+i] = params[i]
        answer = self.session.post('https://vk.com/dev', data=data)
        payload_string = json.loads(answer.text.replace('<!--', ''))['payload'][-1][0]
        data = json.loads(payload_string)
        try:
            return data['response']
        except KeyError:
            print(f"ERROR {data['error']['error_code']}: {data['error']['error_msg']}")

    def get_user(self, user_id):
        if isinstance(user_id, list):
            pass

    def _get_hash(self, method):
        html = self.session.get('https://vk.com/dev/'+method)
        hash_0 = re.findall('onclick="Dev.methodRun\(\'(.+?)\', this\);',html.text)
        if len(hash_0)==0:
            raise not_valid_method("method is not valid")
        self.hashes[method] = hash_0[0]


class VkApiMethod:
    __slots__ = ('_vk', '_method')

    def __init__(self, vk, method=None):
        self._vk = vk
        self._method = method

    def __getattr__(self, method):
        if '_' in method:
            m = method.split('_')
            method = m[0] + ''.join(i.title() for i in m[1:])

        return VkApiMethod(
            self._vk,
            (self._method + '.' if self._method else '') + method
        )

    def __call__(self, **kwargs):
        for k, v in dict.items(kwargs):
            if isinstance(v, (list, tuple)):
                kwargs[k] = ','.join(str(x) for x in v)

        return self._vk.method(self._method, **kwargs)


def interactive_log_in():
    directory = os.path.dirname(CONFIG_PATH)

    if not os.path.exists(directory):
        os.makedirs(directory)

    def get_logpass():
        login = input('Логин (лучше использовать номер телефона): ')
        password = getpass('Пароль: ')
        return login, password

    try:
        with open(CONFIG_PATH, 'r') as file:
            login = file.readline()[:-1]
            password = file.readline()[:-1]
    except:
        login, password = get_logpass()

    while True:
        try:
            vk_s = VkSession(login, password)
        except:
            print('Попробуйте еще раз')
            login, password = get_logpass()
        else:
            with open(CONFIG_PATH, 'w') as file:
                file.write(login + '\n')
                file.write(password + '\n')
            return vk_s

