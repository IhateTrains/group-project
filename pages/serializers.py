from rest_framework import serializers
from .models import SzikPoint


class SzikPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SzikPoint
        fields = ['id', 'city', 'mapLatitude', 'mapLongitude']
