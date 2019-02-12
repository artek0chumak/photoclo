import numpy as np
from django.contrib.postgres.fields import JSONField
from django.db import models
from photo_load.models import Photo

checked_weight = 10
unchecked_weight = 1
embedding_size = 128


class Avatar(models.Model):
    name = models.CharField(max_length=100)
    embedding = JSONField()

    @property
    def get_embedding(self):
        avatar_embedding = np.zeros(embedding_size)
        total_w = 0
        for face in self.face_set:
            next_embedding = face.embedding
            next_embedding = np.array(next_embedding)

            coef = checked_weight if face.user_checked else unchecked_weight
            total_w += coef
            avatar_embedding += coef * next_embedding

        avatar_embedding /= total_w
        return avatar_embedding

    def save(self, *args, **kwargs):
        self.embedding = self.get_embedding()
        super(Avatar, self).save(*args, **kwargs)


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
