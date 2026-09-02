from rest_framework import serializers


class CreateProductRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.FloatField()
    stock = serializers.IntegerField()
