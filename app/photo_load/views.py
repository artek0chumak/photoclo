from face_recognition.async_fd_runner import get_faces
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from .models import Photo, PhotoInfo
from .serializers import PhotoSerializer


class PhotoView(viewsets.GenericViewSet):
    def list(self, request, pk=None):
        offset = int(request.query_params['offset'])
        limit = int(request.query_params['limit'])
        size = request.query_params['size']
        user = request.user

        photos = PhotoInfo.objects.filter(photo__owner=user)\
            .order_by('-time_created').values('photo')

        if len(photos) < offset:
            return Response({'error': "Offset is too large"},
                            status=HTTP_400_BAD_REQUEST)
        photos = Photo.objects.filter(id__in=photos)[offset:offset + limit]

        client_photos = [{'url': getattr(photo, '{0}_size'.format(size)).url,
                          'height': photo.photoinfo.height,
                          'width': photo.photoinfo.width,
                          'id': photo.id}
                         for photo in photos]

        return Response({'count': len(client_photos), 'photos': client_photos},
                        status=HTTP_200_OK)

    def retrieve(self, request, pk):
        photo = Photo.objects.filter(owner=request.user).filter(id=pk)

        if len(photo) == 0:
            return Response({}, status=HTTP_404_NOT_FOUND)

        return Response({'url': photo[0].o_size.url}, status=HTTP_200_OK)

    def destroy(self, request, pk):
        photo = Photo.objects.filter(owner=request.user).filter(id=pk)

        if len(photo) == 0:
            return Response({}, status=HTTP_404_NOT_FOUND)

        photo[0].delete()
        return Response(status=HTTP_200_OK)

    def create(self, request, pk=None):
        data = request.data
        status_list = []
        for item in request.data.getlist('images[]'):
            data['original'] = item
            data['owner'] = request.user.id
            data['user'] = request.user

            photo_serializer = PhotoSerializer(data=data)

            if photo_serializer.is_valid():
                photo = photo_serializer.create(validated_data=data)
                get_faces.apply_async((photo.id, request.user.id),
                                      countdown=2)
                status_list.append('Success')
            else:
                status_list.append('Fail')
        return Response({'status': status_list}, HTTP_201_CREATED)

    @action(detail=True, methods=['GET'])
    def download(self, request, pk=None):
        photo = Photo.objects.filter(owner=request.user).filter(id=pk)

        if len(photo) == 0:
            return Response({}, status=HTTP_404_NOT_FOUND)

        return Response({'url': photo[0].original.url}, status=HTTP_200_OK)

