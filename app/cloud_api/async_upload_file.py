import requests
from celery import Celery
from photo_load.models import Photo

from .models import YAtokens, StatusCode

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def upload_file(photo_id, status_code=None):
    photo = Photo.objects.filter(id=photo_id).first()
    ya_token = YAtokens.objects.filter(user=photo.owner).first()
    file_path = photo.temp_original
    if status_code is None:
        status_code = StatusCode.objects.create(photo=photo,
                                                temp_path=file_path,
                                                is_loaded=False)
    with open(file_path) as file:
        r = requests.get('https://cloud-api.yandex.net/v1/disk/resources'
                         '/upload', {'path': photo.cloud_original},
                         headers={'Authorization':
                                  'OAuth {0}'.format(ya_token)})
        data = r.json()
        url = data['href']
        r = requests.put(url, file)

    if r.status_code in (200, 202):
        status_code.is_loaded = True
    else:
        status_code.is_error = True
        status_code.error_description = \
            '{} - {}'.format(r.status_code,
                             requests.status_codes._codes[r.status_code])
    status_code.save()

    return r.status_code
