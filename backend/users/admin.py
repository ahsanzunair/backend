from django.contrib import admin
from .models import User, AdminProfile, JobseekerProfile, EmployerProfile

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username", "email", "phone_number", "full_name", "role", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "role", "gender")
    search_fields = ("username", "phone_number", "is_active", "role", "gender")
    ordering = ("created_at",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "phone_number", "gender", "date_of_birth", "profile_pic")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "phone_number", "password1", "password2", "role", "gender", "date_of_birth", "profile_pic", "is_active", "is_staff", "is_superuser")}
        )
    )



class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_super_admin', 'can_manage_users', 'can_manage_jobs')
    search_fields = ('user__username',)


class JobseekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_position', 'experience', 'expected_salary', 'location', 'profile_completed')
    search_fields = ('user__username', 'skills', 'current_company', 'location')


class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'industry', 'company_size', 'location', 'is_verified')
    search_fields = ('company', 'user__username', 'industry', 'location')


admin.site.register(User, UserAdmin)
admin.site.register(AdminProfile, AdminProfileAdmin)
admin.site.register(JobseekerProfile, JobseekerProfileAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)