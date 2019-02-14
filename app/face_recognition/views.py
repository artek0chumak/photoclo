from photo_load.models import Photo
from photo_load.serializers import PhotoSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .async_find_probable_avatars import get_probable_avatars
from .models import Face, Avatar, ProbAvatar
from .serializers import FaceSerializer, AvatarSerializer, ProbAvatarSerializer


class FaceView(viewsets.ViewSet):
    def retrieve(self, request, pk):
        faces = Face.objects.filter(photo__owner=request.user).filter(photo=pk)
        if len(faces) == 0:
            return Response({}, status=HTTP_204_NO_CONTENT)
        answer = FaceSerializer(faces, many=True)
        return Response({'faces': answer.data}, status=HTTP_200_OK)

    def update(self, request, pk=None):
        new_avatar = request.data['new_avatar']
        face_id = request.data['face']
        face = Face.objects.filter(photo__owner=request.user).filter(id=face_id)
        if len(face) == 0:
            return Response({}, status=HTTP_404_NOT_FOUND)
        face = face.first()
        face.avatar = Avatar.objects.filter(id=new_avatar).first()
        face.user_checked = True
        face.save()
        return Response({'new_face': FaceSerializer(face).data},
                        status=HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def suggest(self, request, pk):
        faces = Face.objects.filter(photo__owner=request.user).filter(id=pk)
        query = request.query_params('query')

        if len(faces) == 0:
            return Response(status=HTTP_204_NO_CONTENT)

        if len(query) == 0:
            prob_avatars = ProbAvatar.objects.filter(face__in=faces)\
                .filter(avatar__name__isnull=False).order_by('place')
            answer = ProbAvatarSerializer(prob_avatars, many=True).data
        else:
            avatars = Avatar.objects.filter(name__icontains=query)
            answer = AvatarSerializer(avatars, many=True).data

        return Response({'avatar': answer}, status=HTTP_200_OK)


class AvatarView(viewsets.ViewSet):
    def list(self, request, pk=None):
        avatars = Avatar.objects.filter(face__photo__owner=request.user).\
            distinct()
        if len(avatars) == 0:
            return Response({}, status=HTTP_204_NO_CONTENT)
        answer = AvatarSerializer(avatars, many=True)
        return Response({"avatars": answer.data}, status=HTTP_200_OK)

    def create(self, request, pk=None):
        faces = Face.objects.filter(photo__owner=request.user)
        face = faces.filter(id=request.data['face_id']).first()
        name = request.data['name']

        avatar_serializer = AvatarSerializer(data={'name': name,
                                                   'face': face.id})

        if avatar_serializer.is_valid():
            avatar_serializer.save()
            get_probable_avatars.apply_async((request.user.id,))
            return Response(avatar_serializer.data, status=HTTP_201_CREATED)
        else:
            return Response({}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk):
        avatars = Avatar.objects.filter(face__photo__owner=request.user)
        new_name = request.data['new_name']
        if len(avatars.filter(name=new_name)) > 0:
            face = Face.objects.filter(photo__owner=request.user)\
                .filter(id=request.data['face']).first()
            face.avatar = avatars.filter(name=new_name).first()
            face.user_checked = True
            face.save()

            return Response({'updated face': FaceSerializer(face).data},
                            HTTP_200_OK)

        avatar = avatars.filter(id=pk).first()

        if len(avatar) == 0:
            return Response({}, status=HTTP_404_NOT_FOUND)
        avatar = avatar.first()

        avatar.name = new_name
        avatar.save()
        face = Face.objects.filter(photo__owner=request.user)\
            .filter(id=request.data['face']).first()
        face.user_checked = True
        face.save()

        get_probable_avatars.apply_async((request.user.id,))

        return Response({'updated_avatar': AvatarSerializer(avatar).data},
                        status=HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def photos(self, request, pk):
        photos = Photo.objects.filter(owner=request.user)\
            .filter(face__avatar=pk)
        if len(photos) == 0:
            return Response({}, status=HTTP_204_NO_CONTENT)
        return Response({'photos': PhotoSerializer(photos, many=True).data},
                        status=HTTP_200_OK)
