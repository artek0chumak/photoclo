import requests
from celery import Celery
from photo_load.models import Photo

from .models import YAtokens, StatusCode

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def upload_file(photo_id, status_code=None):
    photo = Photo.objects.filter(id=photo_id).first()
    ya_token = YAtokens.objects.filter(user=photo.owner).first()
    headers = {'Authorization': 'OAuth {0}'.format(ya_token.token)}
    file_path = photo.temp_original
    if status_code is None:
        status_code = StatusCode.objects.create(photo=photo,
                                                temp_path=file_path,
                                                is_loaded=False)
    with open(file_path, 'rb') as file:
        r = requests.get('https://cloud-api.yandex.net/v1/disk/resources'
                         '/upload', {'path': photo.cloud_original},
                         headers=headers)

        data = r.json()
        if data.get('error', '') == 'DiskPathDoesntExistsError':
            requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                         params={'path': 'photoclo'}, headers=headers)
            r = requests.get('https://cloud-api.yandex.net/v1/disk/resources'
                             '/upload', {'path': photo.cloud_original},
                             headers=headers)
            data = r.json()

        url = data['href']
        r = requests.put(url, data=file.read())

    if r.status_code in (200, 202, 201):
        status_code.is_loaded = True
        status_code.remove_file()
    else:
        status_code.is_error = True
        status_code.error_description = \
            '{} - {}'.format(r.status_code,
                             requests.status_codes._codes[r.status_code])
    status_code.save()

    return r.status_code


@app.task
def delete_file(cloud_path, token):
    requests.delete('https://cloud-api.yandex.net/v1/disk/resources',
                    params={'path': cloud_path},
                    headers={'Authorization': 'OAuth {0}'.format(token)})
