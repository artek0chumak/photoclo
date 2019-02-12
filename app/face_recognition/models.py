from django.contrib.postgres.fields import JSONField
from django.db import models

from photo_load.models import Photo


class Avatar(models.Model):
    name = models.CharField(max_length=100)
    embedding = JSONField()


class Face(models.Model):
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    embedding = JSONField()
    bounding_box = JSONField()
    user_checked = models.BooleanField(default=False)


class ProbAvatar(models.Model):
    face = models.OneToOneField(Face, on_delete=models.CASCADE)
    avatar = models.OneToOneField(Avatar, on_delete=models.CASCADE)
    place = models.IntegerField()

