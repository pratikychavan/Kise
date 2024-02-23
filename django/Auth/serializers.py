from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    
    class Meta:
        model = User
    
    def validate_username(self, username):
        assert not User.objects.filter(username=username).exists(), f"Username {username} already in use"
        return username
    
    def validate_email(self, email):
        assert not User.objects.filter(email=email).exists(), f"Email {email} already in use"
        return email

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_username(self, username):
        assert User.objects.filter(username=username).exists(), f"No user with username '{username}' found."
        return username
    
    def validate(self, data):
        return authenticate(**data)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        # Implement logic to send password reset email here
        # You can use Django's built-in PasswordResetTokenGenerator to generate a token

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link")

        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError("Invalid reset link")

        return data

    def save(self):
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(self.validated_data['uidb64'])))
        user.set_password(self.validated_data['password'])
        user.save()
        return user
