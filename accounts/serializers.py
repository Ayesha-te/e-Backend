from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'role', 'phone', 'company_name'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'company_name']