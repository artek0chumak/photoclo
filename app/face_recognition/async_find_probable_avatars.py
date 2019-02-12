import numpy as np
from celery import Celery

from .models import Face, Avatar, ProbAvatar

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def get_probable_avatars(face_id, user_id):
    top_avatars_num = 5

    face_input = Face.objects.filter(photo__owner=user_id).\
        filter(id=face_id).first()
    embedding_input = face_input.embedding
    embedding_input = np.array(embedding_input)

    probable_avatars = Avatar.objects.filter(photo__owner=user_id).\
        order_by('id')
    probable_emb = probable_avatars.values('embedding')
    probable_avatars = list(probable_avatars)

    probable_emb = np.array(probable_emb)
    probable_dist = np.linalg.norm(probable_emb - embedding_input, axis=1)

    for i in np.argpartition(probable_dist, range(top_avatars_num)):
        avatar = probable_avatars[i]
        ProbAvatar.objects.create(avatar=avatar, face=face_input, place=i)\
            .save()


def get_avatar_embedding(avatar_id, user_id):
    checked_w = 10
    unchecked_w = 1
    embedding_size = 128

    avatar_faces = Face.objects.filter(photo__owner=user_id)\
        .filter(avatar=avatar_id)

    avatar_embedding = np.zeros(embedding_size)
    total_w = 0
    for face in avatar_faces:
        next_embedding = face.embedding
        next_embedding = np.array(next_embedding)

        coef = checked_w if face.user_checked else unchecked_w
        total_w += coef
        avatar_embedding += coef * next_embedding

    avatar_embedding /= total_w
    return avatar_embedding
