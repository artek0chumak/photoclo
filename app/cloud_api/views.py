import os

import requests
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_503_SERVICE_UNAVAILABLE,
)
from rest_framework.viewsets import ViewSet
from yaml import load

from .async_upload_file import upload_file
from .models import YAtokens, StatusCode
from .serializers import StatusCodeSerializer

with open(os.path.join(settings.BASE_DIR, 'configs', 'ya_disk_config.yaml'))\
        as file:
    ya_disk_client = load(file)


class TokenView(ViewSet):
    @action(methods=['GET'], detail=False, url_path='code')
    def get_access_code(self, request, pk=None):
        tokens = YAtokens.objects.filter(user=request.user)
        if len(tokens) > 0:
            return Response(status=HTTP_200_OK)
        url = 'https://oauth.yandex.ru/authorize?response_type=code' \
              '&client_id={0}'.format(ya_disk_client['client-id'])
        return Response({'url': url}, status=HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='token')
    def get_token(self, request, pk=None):
        try:
            code = request.query_params['code']
        except UnsupportedMediaType as error:
            error = request.query_params['error']
            error_description = request.query_params['error_description']
            return Response({'error': error, 'error_description':
                             error_description}, status=HTTP_400_BAD_REQUEST)
            # Not sure about HTTP code for this request.

        r = requests.post('https://oauth.yandex.ru/token',
                          {'grant_type': 'authorization_code',
                           'code': code,
                           'client_id': ya_disk_client['client-id'],
                           'client_secret': ya_disk_client['client-secret']})

        data = r.json()
        if data.get('token', None) is None:
            Response(data, status=HTTP_400_BAD_REQUEST)
        user_token = YAtokens.objects.create(user=request.user,
                                             token=data['access_token'],
                                             expires_in=data['expires_in'])
        user_token.save()
        return Response({}, status=HTTP_201_CREATED)


class StatusCodeView(ViewSet):
    def retrieve(self, request, pk):
        status_code = StatusCode.objects.filter(photo__owner=request.user)\
            .filter(photo=pk)
        if len(status_code) == 0:
            return Response(status=HTTP_404_NOT_FOUND)
        status_code = status_code.first()
        sc_serializer = StatusCodeSerializer(status_code)
        if status_code.is_loaded:
            status_code.delete()
            return Response({'status_code': sc_serializer},
                            status=HTTP_201_CREATED)
        else:
            return Response({'status_code': sc_serializer},
                            status=HTTP_503_SERVICE_UNAVAILABLE)

    def update(self, request, pk):
        status_code = StatusCode.objects.filter(photo__owner=request.user)\
            .filter(photo=pk)
        if len(status_code) == 0:
            return Response(status=HTTP_404_NOT_FOUND)
        status_code = status_code.first()
        sc_serializer = StatusCodeSerializer(status_code)
        if status_code.is_loaded:
            status_code.delete()
            return Response({'status_code': sc_serializer},
                            status=HTTP_201_CREATED)
        else:
            upload_file.apply_async((pk, None, None, status_code),
                                    countdown=5)
            return Response({'status_code': 'retry'}, status=HTTP_200_OK)
