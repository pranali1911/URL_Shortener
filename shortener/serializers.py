from rest_framework import serializers
from .models import URL
from .utils import base62_encode

class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = ["id", "original_url", "short_code", "custom_alias", "expires_at", "status", "created_at"]
        read_only_fields = ["id", "short_code", "created_at"]

    def create(self, validated_data):
        custom_alias = validated_data.get("custom_alias")

        url = URL.objects.create(**validated_data)

        if custom_alias:
            url.short_code = custom_alias
        else:
            url.short_code = base62_encode(url.id)

        url.save()

        return url