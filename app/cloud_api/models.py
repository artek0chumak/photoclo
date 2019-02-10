import os

from django.contrib.auth import get_user_model
from django.db import models
from photo_load.models import Photo

User = get_user_model()


class YAtokens(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    expires_in = models.IntegerField(null=True)


class StatusCode(models.Model):
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE,
                                 primary_key=True)
    temp_path = models.FilePathField()
    is_loaded = models.BooleanField()
    is_error = models.NullBooleanField()
    error_description = models.CharField(max_length=200, null=True)

    def delete(self, using=None, keep_parents=False):
        os.remove(self.temp_path)
        return super(StatusCode, self).delete(using=using,
                                              keep_parents=keep_parents)


class TempState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=200)
