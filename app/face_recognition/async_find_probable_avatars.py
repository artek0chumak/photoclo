import numpy as np
from celery import Celery

from .models import Face, Avatar, ProbAvatar

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def get_probable_avatars_user(user_id):
    for face in Face.objects.filter(photo__owner_id=user_id):
        if not face.user_checked:
            get_probable_avatars_face(face, user_id)


def get_probable_avatars_face(face_input, user_id):
    top_avatars_num = 5

    embedding_input = face_input.embedding
    embedding_input = np.array(embedding_input)

    probable_avatars = Avatar.objects.filter(photo__owner=user_id).\
        order_by('id')
    probable_emb = probable_avatars.values('embedding')
    probable_avatars = list(probable_avatars)

    probable_emb = np.array(probable_emb)
    probable_dist = np.linalg.norm(probable_emb - embedding_input, axis=1)

    ProbAvatar.objects.filter(face=face_input).delete()

    for i in np.argpartition(probable_dist, range(top_avatars_num)):
        avatar = probable_avatars[i]
        ProbAvatar.objects.create_or_update(avatar=avatar, face=face_input,
                                            place=i).save()

