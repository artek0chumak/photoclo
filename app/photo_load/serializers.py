from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Photo, PhotoInfo

User = get_user_model()


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('id', 'owner', 'temp_original', 'cloud_original',)

    def create(self, validated_data):
        owner = User.objects.filter(id=validated_data['owner']).first()
        data = validated_data
        photo = \
            Photo.objects.create(owner=owner,
                                 temp_original=data['temp_original'],
                                 cloud_original=data['cloud_original'],
                                 filename=data['filename'])
        photo.save()

        photo_info = PhotoInfo.objects.create(photo=photo)
        photo_info.save()
        return photo
