import numpy as np
from celery import Celery

from .models import Face, Avatar, ProbAvatar

app = Celery('tasks', broker='pyamqp://guest@localhost//')


max_top_avatars_num = 5


@app.task
def get_probable_avatars(face_id, user_id):
    face_input = Face.objects.filter(photo__owner=user_id).\
        filter(id=face_id).first()

    embedding_input = face_input.embedding
    embedding_input = np.array(embedding_input)

    probable_avatars = Avatar.objects.filter(face__photo__owner=user_id).\
        order_by('id')
    probable_avatars = list(probable_avatars)
    top_avatars_num = min(max_top_avatars_num, len(probable_avatars))

    probable_emb = np.array([prb_avatar.embedding for prb_avatar in
                            probable_avatars])
    probable_dist = np.linalg.norm(probable_emb - embedding_input, axis=1)

    ProbAvatar.objects.filter(face=face_input).delete()
    probable_avatars_top = \
        np.argpartition(probable_dist, range(top_avatars_num))[:top_avatars_num]

    j = 0
    for i in probable_avatars_top:
        j += 1
        avatar = probable_avatars[i]
        print('{} {} {}'.format(avatar, face_input, j))
        ProbAvatar.objects.create(avatar=avatar, face=face_input,
                                  place=j).save()

