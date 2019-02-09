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

from app.photo_load.models import Photo
from app.photo_load.serializers import PhotoSerializer
from .models import Face, Avatar
from .serializers import FaceSerializer, AvatarSerializer


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
            return Response(avatar_serializer.data, status=HTTP_201_CREATED)
        else:
            return Response({}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk):
        avatar = Avatar.objects.filter(face__photo__owner=request.user).\
            filter(id=pk)
        if len(avatar) == 0:
            return Response({}, status=HTTP_404_NOT_FOUND)
        avatar = avatar.first()

        new_name = request.data['new_name']
        avatar.name = new_name
        avatar.save()
        face = Face.objects.filter(photo__owner=request.user)\
            .filter(id=request.data['face']).first()
        face.user_checked = True
        face.save()
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
