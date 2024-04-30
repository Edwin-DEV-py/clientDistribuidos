from rest_framework import serializers

class UserCredentialsSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserDataSerializer(serializers.Serializer):
    username = serializers.CharField()
    name = serializers.CharField()
    email = serializers.CharField()
    age = serializers.CharField()
    password = serializers.CharField()