from rest_framework import generics,  permissions, status
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from .models import User, AdminProfile, JobseekerProfile, EmployerProfile
from .serializers import (
    UserRegistrationSerializer,
    TokenObtainPairSerializer,
    UserSerializer,
    UserWithProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    JobseekerProfileSerializer,
    EmployerProfileSerializer,
    AdminProfileSerializer
)


# Create your views here.


def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("User is not Active")
    
    refresh = RefreshToken.for_user(user)
    
    return{
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserRegistrationView(generics.CreateAPIView):
    renderer_classes = [UserRenderer]
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)

        return Response(
            {
                "token": token,
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
                "redirect_to": "/auth/login"
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = []
    renderer_classes = [UserRenderer]  
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Please provide both email and password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        
        user = authenticate(request, email=email, password=password)
        token = get_tokens_for_user(user)
        
        if not user:
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is active
        if not user.is_active:
            return Response(
                {"detail": "Account is inactive. Please contact administrator."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # role based redirect
        if user.role == "admin":
            redirect_to = "/admin/dashboard"
        elif user.role == "employer":
            redirect_to = "/employer/employer-dashboard"
        elif user.role == "jobseeker":  
            redirect_to = "/jobs"

        return Response({
            "token": token,
            "message": "Login successful",
            "redirect_to": redirect_to,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_200_OK)