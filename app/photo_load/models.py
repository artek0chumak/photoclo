import hashlib
import subprocess
import sys
from datetime import datetime
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from wand.image import Image

sizes = {'z': 1080, 'y': 807, 'x': 604, 'm': 320, 's': 100}


def get_upload_path(instance, filename):
    return instance.get_upload_path(filename, '')


def get_upload_path_size_o(instance, filename):
    return instance.get_upload_path(filename, 'o')


def get_upload_path_size_z(instance, filename):
    return instance.get_upload_path(filename, 'z')


def get_upload_path_size_y(instance, filename):
    return instance.get_upload_path(filename, 'y')


def get_upload_path_size_x(instance, filename):
    return instance.get_upload_path(filename, 'x')


def get_upload_path_size_m(instance, filename):
    return instance.get_upload_path(filename, 'm')


def get_upload_path_size_s(instance, filename):
    return instance.get_upload_path(filename, 's')


class Photo(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    temp_original = models.TextField(null=True)
    cloud_original = models.TextField()
    filename = models.TextField()
    o_size = models.ImageField(upload_to=get_upload_path_size_o)
    z_size = models.ImageField(upload_to=get_upload_path_size_z)
    y_size = models.ImageField(upload_to=get_upload_path_size_y)
    x_size = models.ImageField(upload_to=get_upload_path_size_x)
    m_size = models.ImageField(upload_to=get_upload_path_size_m)
    s_size = models.ImageField(upload_to=get_upload_path_size_s)
    checked = models.NullBooleanField()

    def get_upload_path(self, filename, size):
        temp = hashlib.sha256(self.owner.username.encode('utf-8'))
        return '{0}/{1}_{2}'.format(temp.hexdigest(), size, filename)

    def save(self, *args, **kwargs):
        with Image(filename=self.temp_original) as image:
            image.format = 'jpeg'
            image.compression_quality = 90

            name_no_ext = ''.join(self.filename.split('.')[:-1])
            shape = image.size
            io_stream = BytesIO()
            image.resize(*shape)
            image.save(io_stream)
            io_stream.seek(0)
            temp = InMemoryUploadedFile(io_stream, 'ImageField',
                                        "{0}.jpeg".format(name_no_ext),
                                        'image/jpeg',
                                        sys.getsizeof(io_stream), None)

            self.o_size = temp

        for size in sizes:
            setattr(self, '{0}_size'.format(size), self.compress(size))

        return super(Photo, self).save(*args, **kwargs)

    def compress(self, size):
        with Image(blob=self.o_size.file) as image:
            image.format = 'jpeg'
            image.compression_quality = 90
            file_name = ''.join(self.o_size.name.split('.')[:-1])
            io_stream = BytesIO()
            if size == 'o':
                shape = image.size
            else:
                max_side = max(image.size)
                if max_side < sizes[size]:
                    max_side = sizes[size]
                proc = sizes[size] / max_side
                shape = (int(image.width * proc), int(image.height * proc))
            image.resize(*shape)
            image.save(io_stream)
            io_stream.seek(0)
            sized = InMemoryUploadedFile(io_stream, 'ImageField',
                                         "{0}.jpeg".format(file_name),
                                         'image/jpeg', sys.getsizeof(io_stream),
                                         None)
            return sized


class PhotoInfo(models.Model):
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE,
                                 primary_key=True)
    time_created = models.DateTimeField()
    width = models.IntegerField()
    height = models.IntegerField()

    def save(self, *args, **kwargs):
        for size_type in sizes:
            size = getattr(self.photo, '{0}_size'.format(size_type))
            subprocess.run(['exiftool', "-overwrite_original", '-TagsFromFile',
                            self.photo.temp_original, size.path],
                           stdout=subprocess.PIPE)

        with Image(blob=self.photo.o_size.file) as image:
            self.width, self.height = image.size

        result = subprocess.run(['exiftool', '-dateTimeOriginal',
                                self.photo.temp_original],
                                stdout=subprocess.PIPE)

        result = result.stdout.decode('utf-8')
        if len(result) == 0:
            self.time_created = datetime.now()
        else:
            dt = (':'.join(result.split(':')[1:])).split('+')[0]
            dt = dt.strip()
            self.time_created = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')

        super(PhotoInfo, self).save(*args, **kwargs)
