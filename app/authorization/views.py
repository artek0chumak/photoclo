from django.contrib.auth import login, logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.viewsets import ViewSet

from .serializers import UserSerializer


class UserView(ViewSet):
    @action(methods=['post'], detail=False)
    def singin(self, request, pk=None):
        user_serializer = UserSerializer(data=request['data'])
        if user_serializer.is_valid():
            user = user_serializer.save()
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_200_OK)
        else:
            return Response(status=HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=False)
    def singup(self, request, pk=None):
        user_serializer = UserSerializer(data=request['data'])
        if user_serializer.is_valid():
            user = user_serializer.save()
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=False)
    def signout(self, request, pk=None):
        logout(request)
        return Response(status=HTTP_200_OK)
