from tqdm import tqdm
import json
import os.path
from datetime import datetime
import requests


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def upload(self, file_name: str, url: str):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        params = {"path": "photo_backup"}
        response = requests.get(upload_url, headers=headers, params=params)
        if response.json().get('description') == 'Resource not found.':
            print("Нет такой папки ... создаю...")
            response = requests.put(upload_url, headers=headers, params=params)
        params = {"path": "photo_backup/" + file_name, "url": url}
        response = requests.post(upload_url + "upload", headers=headers, params=params)


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, version):
        with open('token.txt', 'r') as file_object:
            token = file_object.readline().strip()
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photo(self, user_id=None):
        groups_url = self.url + 'photos.get'
        groups_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        }
        res = requests.get(groups_url, params={**self.params, **groups_params})
        return res.json()


def backup_photo(id_vk: str, token_yd: str, count_photo=5, ver_vk='5.131'):
    vk_client = VkUser(ver_vk)
    uploader = YaUploader(token_yd)
    rez = vk_client.get_photo(id_vk)
    list_foto = rez['response']['items']
    path = os.getcwd() + '\\' + 'json_files\\'
    list_name_photo = set()
    if not os.path.isdir(path):
        os.mkdir(path)
    with tqdm(total=count_photo, desc="Processing") as pbar:
        for indx, it in enumerate(list_foto):
            if indx == count_photo:
                break
            max_size = 0
            json_file = []
            for l in it['sizes']:
                check_size = l['height'] * l['width']
                if check_size > max_size or max_size == 0:
                    max_size = check_size
                    url = l['url']
                    count_likes = it['likes']['count']
                    size = l['type']
            dat = datetime.utcfromtimestamp(int(it['date'])).strftime('%Y-%m-%d')
            if count_likes not in list_name_photo:
                file_name = str(count_likes)
                uploader.upload(str(count_likes), url)
            else:
                file_name = str(count_likes) + '_' + dat
                uploader.upload(str(count_likes) + '_' + dat, url)
            list_name_photo.add(count_likes)

            json_file.append({"file_name": file_name + '.jpg', "size": size})

            with open(path + file_name + '.json', 'w') as f:
                json.dump(json_file, f, indent=2)

            pbar.update(1)



if __name__ == '__main__':
# в файл token.txt необходимо добавить токет от VK
    # в функцию передаем реальный ид пользователя vk, токен яндекса и количество фотографий (по умолчанию 5)
    backup_photo('1', '123456')