from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def is_valid(self, raise_exception=False):
        user = authenticate(username=self.username, password=self.password)
        if not user:
            return False
        return super(UserSerializer, self).is_valid(
            raise_exception=raise_exception)
