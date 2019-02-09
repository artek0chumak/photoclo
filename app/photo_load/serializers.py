from rest_framework import serializers

from .models import Photo, PhotoInfo


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('id', 'original', 'owner')

    def create(self, validated_data):
        original = validated_data['original']
        owner = validated_data['user']
        photo, _ = Photo.objects.update_or_create(original=original,
                                                  owner=owner)
        PhotoInfo.objects.update_or_create(photo=photo)
        return photo
