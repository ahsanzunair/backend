from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.utils.text import slugify
from .validators import validate_file_extension, ValidationError


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValidationError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("jobseeker", "Jobseeker"),
        ("employer", "Employer"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    phone_number = PhoneNumberField(region="PK", blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", validators=[validate_file_extension], blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="jobseeker")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"] 

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f"{self.username}-{self.id}")
        return super().save(*args, **kwargs)
        if "-" not in self.slug:
            self.slug = slugify(f"{self.full_name}-{self.id}")
            super().save(update_fields=["slug"])
            
    
    def clean(self):
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future")

    def __str__(self):
        return f"{self.username} ({self.role})"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, related_name="admin_profile", on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=True)
    can_manage_jobs = models.BooleanField(default=True)

    def __str__(self):
        return f"Admin: {self.user.full_name}"


class JobseekerProfile(models.Model):
    user = models.OneToOneField(User, related_name="jobseeker_profile", on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    resume = models.FileField(upload_to="resumes/", validators=[validate_file_extension], blank=True, null=True)
    skills = models.TextField(blank=True)
    experience = models.IntegerField(default=0)
    current_position = models.CharField(max_length=100, blank=True)
    current_company = models.CharField(max_length=100, blank=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True)
    education = models.TextField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"JobSeeker: {self.user.username}"


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, related_name="employer_profile", on_delete=models.CASCADE)
    company = models.CharField(max_length=200)
    about_company = models.TextField(blank=True)
    company_website = models.URLField(blank=True)
    company_logo = models.ImageField(
    upload_to="company_logos/",
    validators=[validate_file_extension],
    blank=True, null=True
    )
    industry = models.CharField(max_length=200, blank=True)
    company_size = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return f"Employer: {self.company}"