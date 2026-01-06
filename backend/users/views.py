from django.shortcuts import render
from rest_framework import generics,  permissions, status
from rest_framework.response import Response
from .models import User, AdminProfile, JobseekerProfile, EmployerProfile
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserWithProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    JobseekerProfileSerializer,
    EmployerProfileSerializer,
    AdminProfileSerializer
)


# Create your views here.


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )
