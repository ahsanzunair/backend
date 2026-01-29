from rest_framework import generics,  permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from django.contrib.auth import authenticate 
from .renderers import UserRenderer
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



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            
            if not refresh_token:
                return Response(
                    {"detail": "Refresh Token is Required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"Message": "Logout Successfull"},
                status=status.HTTP_205_RESET_CONTENT
            )
            
        except Exception as e:
            return Response(
                {"detail": "Invalid token or already logged out"},
                status=status.HTTP_400_BAD_REQUEST
            )


def get_profile_and_serializer(user):
        if user.role == "jobseeker":
            return(
                JobseekerProfile.objects.get(user=user), JobseekerProfileSerializer
            )
        elif user.role == "employer":
            return(
                EmployerProfile.objects.get(user=user), EmployerProfileSerializer
            )
        elif user.role == "admin":
            return(
                AdminProfile.objects.get(user=user), AdminProfileSerializer
            )
        return None, None

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]
    
    def get(self, request):
        profile, serializer_class = get_profile_and_serializer(request.user)
        
        if not profile:
            return Response(
                {"detail": "Profile not Found"},status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = serializer_class(profile)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def patch(self, request):
        profile, serializer_class = get_profile_and_serializer(request.user)
        
        if not profile:
            return Response(
                {"detail": "Profile not Found"}
            )
        
        serializer = serializer_class(
            profile,
            data = request.user,
            partial = True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]
    
    def put(self, request):
        serializer = ProfileUpdateSerializer(
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            user = request.user
            data = serializer.validated_data
            
            for field in [
                "first_name",
                "last_name",
                "phone_number",
                "gender",
                "date_of_birth",
                "profile_pic",
            ]:
                if field in data:
                    setattr(user, field, data[field])
            
            user.save()
            
            return Response(
                {
                    "message": "profile Updated Successfully",
                    "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": str(user.phone_number) if user.phone_number else None,
                    "gender": user.gender,
                    "date_of_birth": user.date_of_birth,
                    "profile_pic": request.build_absolute_uri(user.profile_pic.url) if user.profile_pic else None,
                }

                },
                status=status.HTTP_200_OK
            )
            
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]
    
    def post(self, request):
        seriallizer = ChangePasswordSerializer(
    data=request.data,
    context={"request":request}                         
    )
        
        if seriallizer.is_valid():
            user = request.user
            new_password = seriallizer.validated_data["new_password"]
            
            user.set_password(new_password)
            user.save()
            
            # RefreshToken.for_user(user)
            
            return Response(
                {"message": "Password Changed Successfully"},
                status=status.HTTP_200_OK
            )
            
        return Response(
            seriallizer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )