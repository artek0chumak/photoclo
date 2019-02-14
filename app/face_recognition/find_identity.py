import numpy as np
from celery import Celery

from .async_find_probable_avatars import get_probable_avatars
from .models import Face, Avatar

app = Celery('tasks', broker='pyamqp://guest@localhost//')


# if we find a face, such that the distance between the found face and the
# given face is smaller than a threshold, than we suppose it is the same avatar
threshold = 0.9


@app.task
def get_identity(face_id, user_id):
    face_input = Face.objects.filter(photo__owner=user_id)\
        .filter(id=face_id).first()
    faces_query = Face.objects.filter(photo__owner=user_id)\
        .filter(avatar__isnull=False)

    embedding_input = face_input.embedding
    embedding_input = np.array(embedding_input)
    avatar_id = -1
    avatar_dist = float('Inf')

    for face in faces_query:
        next_embedding = face.embedding
        next_embedding = np.array(next_embedding)
        norm = np.linalg.norm(embedding_input - next_embedding)
        if norm < avatar_dist:
            avatar_id = face.avatar.id
            avatar_dist = norm

    if avatar_dist < threshold:
        save_avatar(face_id, avatar_id)
    else:
        create_new_avatar(face_id)

    get_probable_avatars(user_id)


def create_new_avatar(face_id):
    avatar = Avatar.objects.create()
    avatar.name = None
    avatar.save()
    face = Face.objects.filter(id=face_id).first()
    face.avatar = avatar
    face.save()
    return avatar.id


def save_avatar(face_id, avatar_id):
    face = Face.objects.filter(id=face_id).first()
    face.avatar = Avatar.objects.filter(id=avatar_id).first()
    face.save()
    return avatar_id



