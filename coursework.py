import requests
import time
from tqdm import tqdm, tqdm_gui, trange
import json


class V_Kontakte:
    def __init__(self, vk_token, album_id, owner_id):
        self.album_id = album_id
        self.owner_id = owner_id
        self.vk_token = vk_token
        self.base_vk_URL = 'https://api.vk.com/method/photos.get'
        self.vk_params = {
            'owner_id': self.owner_id, 'album_id': self.album_id,
            'extended': '1', 'photo_sizes': '1',
            'access_token': vk_token, 'v': '5.131'
        }

    def receive_a_request(self):
        "Запрос на получение фото"
        response = requests.get(
            self.base_vk_URL, params=self.vk_params
        )
        data = response.json()
        return data

    def photo_search(self):
        " Формирование общей информации по фото"
        sort_list_photo = []
        list_likes = []
        list_date = []
        # Сортировка фото
        for respons, item in self.receive_a_request().items():
            for item in item['items']:
                sort_list = (sorted(item['sizes'],
                                    key=lambda i: (i['height'],
                                                   i['width'])))
                sort_list_photo.append(sort_list[-1])
                list_date.append(item['date'])
                # Добавление даты если количество лайков одинаково
                list_likes.append(item['likes']['count'])
        file_overview = []
        some_list_likes = []
        unique_likes = set(list_likes)
        for unique in unique_likes:
            count = 0
            for likes in list_likes:
                if unique == likes:
                    count += 1
                    if count > 1 and likes not in some_list_likes:
                        some_list_likes.append(likes)
        for likes, date, s_list in zip(list_likes, list_date,
                                       sort_list_photo):
            if likes in some_list_likes:
                dict_file_name = {
                    "file_name": f"{likes}.jpg {date}",
                    "size": s_list
                }
            else:
                dict_file_name = {
                    "file_name": f"{likes}.jpg",

                    "size": s_list
                }
            file_overview.append(dict_file_name)
        return file_overview


class Yndex_Disk(V_Kontakte):

    def __init__(self, yd_token, album_id, owner_id):
        super().__init__(yd_token, album_id, owner_id)
        self.yd_token = yd_token
        self.yd_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.yd_token}'
        }
        self.base_vk_URL = 'https://api.vk.com/method/photos.get'
        self.base_yd_url = "https://cloud-api.yandex.net"
        self.vk_params = {
            'owner_id': self.owner_id,
            'album_id': self.album_id,
            'extended': '1', 'photo_sizes': '1',
            'access_token': vk_token, 'v': '5.131'
        }

    def create_folder(self, yd_path):
        "Создание папки на яндекс диске"
        yd_URL = f"{self.base_yd_url}/v1/disk/resources"
        requests.put(f'{yd_URL}?path={yd_path}',
                     headers=self.yd_headers)

    def file_recording_yd(self):
        "Запись файла с информацией по фото"
        list_file_information = []
        photo_upload_list = []
        # Формирование информации для записи в файл
        # и фото для загрузки на яндекс диск
        for i in self.photo_search():
            dict_file_information = {
                'file_name': f"{i['file_name']}",
                'size': i['size']['type']
            }
            dict_file_upload = {
                'photo': i['size']['url'],
                'file_name': i['file_name']
            }
            list_file_information.append(dict_file_information)
            photo_upload_list.append(dict_file_upload)
        with open('File information.json', 'w', newline="") \
                as file:
            json.dump(list_file_information, file, indent=2)
        return photo_upload_list

    def upload_to_yd(self, path):
        "Загрузка фото на яндекс диск"
        self.create_folder('backup_folder')
        upload_url = "https://cloud-api.yandex.net/" \
                     "v1/disk/resources/upload"
        for photo in tqdm(self.file_recording_yd(),
                          desc='Yandex photo upload: '):
            time.sleep(0.33)
            params = {
                'path': f"{path}/{photo['file_name']}",
                "url": photo['photo']
            }
            response = requests.post(upload_url,
                                     headers=self.yd_headers,
                                     params=params)


if __name__ == '__main__':
    yd_token = ''

    vk_token = ''

    yd = Yndex_Disk(yd_token, input('Enter the album id,profile,'
                                    'saved or wall: '),
                    input('Enter owner id: '))

    yd.upload_to_yd('backup_folder')
    