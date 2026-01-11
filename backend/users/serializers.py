from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import User, AdminProfile, JobseekerProfile, EmployerProfile
from .validators import validate_file_extension


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  
    def validate(self, attrs):
        authenticate_kwargs = {
            'username': attrs['email'],
            'password': attrs['password']
        }
        user = authenticate(**authenticate_kwargs)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=False)
    profile_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "full_name",
            "phone_number", "gender", "date_of_birth", "profile_pic",
            "profile_pic_url", "role", "is_active", "created_at", "updated_at",
            "password"
        ]
        read_only_fields = ["created_at", "updated_at", "is_active"]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def get_profile_pic_url(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.url
        return None

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_date_of_birth(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future")
        return value

    def validate_password(self, value):
        if value:
            validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password", "password2", "role", "phone_number", "gender", ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists."})
        
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        
        return attrs
    
    def validate_role(self, value):
        if value not in ["jobseeker", "employer", "admin"]:
            raise serializers.ValidationError("Invalid role")
        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = AdminProfile
        fields = ["id", "user", "user_details", "is_super_admin", "can_manage_users", "can_manage_jobs"]
        read_only_fields = ["user"]

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "email": obj.user.email,
            "full_name": obj.user.full_name,
        }


class JobseekerProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()
    skills_list = serializers.SerializerMethodField()

    class Meta:
        model = JobseekerProfile
        fields = [
            "id", "user", "user_details", "bio", "resume", "resume_url",
            "skills", "skills_list", "experience", "current_position",
            "current_company", "expected_salary", "location", "education",
            "linkedin_profile", "github_profile", "is_active", "profile_completed"
        ]
        read_only_fields = ["user", "is_active"]

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "email": obj.user.email,
            "full_name": obj.user.full_name,
            "phone_number": str(obj.user.phone_number) if obj.user.phone_number else None,
            "gender": obj.user.gender,
        }

    def get_resume_url(self, obj):
        if obj.resume:
            return obj.resume.url
        return None

    def get_skills_list(self, obj):
        if obj.skills:
            return [skill.strip() for skill in obj.skills.split(",") if skill.strip()]
        return []

    def validate_resume(self, value):
        if value:
            try:
                validate_file_extension(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value

    def validate_skills(self, value):
        # Clean and format skills string
        if value:
            skills_list = [skill.strip() for skill in value.split(",") if skill.strip()]
            return ", ".join(skills_list)
        return value


class EmployerProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    company_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = EmployerProfile
        fields = [
            "id", "user", "user_details", "company", "about_company",
            "company_website", "company_logo", "company_logo_url",
            "industry", "company_size", "location", "is_verified",
            "contact_person", "contact_email"
        ]
        read_only_fields = ["user", "is_verified"]

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "email": obj.user.email,
            "full_name": obj.user.full_name,
            "phone_number": str(obj.user.phone_number) if obj.user.phone_number else None,
        }

    def get_company_logo_url(self, obj):
        if obj.company_logo:
            return obj.company_logo.url
        return None

    def validate_company_logo(self, value):
        if value:
            try:
                validate_file_extension(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value

    def validate_company_website(self, value):
        if value and not value.startswith(("http://", "https://")):
            value = "https://" + value
        return value


class UserWithProfileSerializer(serializers.ModelSerializer):
    admin_profile = AdminProfileSerializer(read_only=True)
    jobseeker_profile = JobseekerProfileSerializer(read_only=True)
    employer_profile = EmployerProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    profile_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "full_name",
            "phone_number", "gender", "date_of_birth", "profile_pic",
            "profile_pic_url", "role", "is_active", "created_at", "updated_at",
            "admin_profile", "jobseeker_profile", "employer_profile"
        ]
        read_only_fields = fields

    def get_profile_pic_url(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.url
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    date_of_birth = serializers.DateField(required=False)
    profile_pic = serializers.ImageField(required=False)

    def validate_date_of_birth(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future")
        return value

    def validate_profile_pic(self, value):
        if value:
            try:
                validate_file_extension(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value