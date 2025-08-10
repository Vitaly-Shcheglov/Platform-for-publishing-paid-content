from rest_framework import serializers
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["phone_number", "email", "password", "avatar", "country"]

    def create(self, validated_data):
        user = CustomUser(
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            avatar=validated_data.get('avatar'),
            country=validated_data.get('country'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, data):
        if CustomUser.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError({"phone_number": "Этот номер телефона уже зарегистрирован."})
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Этот email уже зарегистрирован."})

        return data