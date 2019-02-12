from rest_framework import serializers

from .models import Avatar, Face, ProbAvatar


class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Avatar
        fields = ('id', 'name',)


class FaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Face
        fields = ('id', 'avatar', 'photo', 'embedding', 'bounding_box',
                  'user_checked')


class ProbAvatarSerializer(serializers.ModelSerializer):
    avatar_name = serializers.SerializerMethodField()

    class ProbAvatar:
        model = ProbAvatar
        fields = ('face', 'avatar', 'avatar_name', 'place')

    def get_avatar_name(self, obj):
        return obj.avatar.name
