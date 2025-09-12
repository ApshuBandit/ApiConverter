# converter/serializers.py
from rest_framework import serializers

class ConvertSerializer(serializers.Serializer):
    files = serializers.FileField()
    format = serializers.ChoiceField(
        choices=["jpg", "png", "webp"],
        default="webp"
    )
