from rest_framework import serializers

from .models import StatusCode


class StatusCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusCode
        fields = ('photo', 'is_loaded', 'is_error', 'error_description')
