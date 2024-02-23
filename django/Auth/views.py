from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User

from Auth.serializers import RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, LoginSerializer

class Register(APIView):
    def put(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"msg": "Registration Successful"}, status=status.HTTP_201_CREATED)
        return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class PasswordReset(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={
                    "detail": "Password reset e-mail has been sent."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class PasswordResetConfirm(APIView):
    def patch(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = serializer.user
            refresh_token = RefreshToken.for_user(user)
            response = {
                "tokens": {
                    "refresh_token": str(refresh_token),
                    "access_token": str(refresh_token.access_token),
                }
            }
            return Response(
                data={
                    "msg": "Password Reset Successful", 
                    "response": response
                }, 
                status=status.HTTP_201_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Login(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh_token = RefreshToken.for_user(user)
            response = {
                "tokens": {
                    "refresh_token": str(refresh_token),
                    "access_token": str(refresh_token.access_token),
                }
            }
            return Response(
                data={
                    "msg": "Login Successful", 
                    "response": response
                }, 
                status=status.HTTP_201_OK
            )
        return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)