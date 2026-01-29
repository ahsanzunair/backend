from rest_framework import serializers
from django.utils.text import slugify
from django.utils import timezone
from .models import Job

class JobListSerializer(serializers.ModelSerializer):
    days_ago = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ["id", "title", "slug", "description", "requirements", "skills", "benefits", "experience", "company", "location", "job_type", "employement_type", "experience_level", "salary_range", "posted_date", "days_ago", "is_new", "status"]
        read_only_fields = ["slug", "posted_date"]
    
    def get_days_ago(self, obj):
        """Calculate how many days ago the job was posted"""
        
        if obj.posted_date:
            delta = timezone.now() - obj.posted_date
            return delta.days
        return None
    
    def get_is_new(self, obj):
        """Check if job was posted within last 7 days"""
        
        if obj.posted_date:
            delta = timezone.now() - obj.posted_date
            return delta.days <= 7
        return False 


class JobDetailSerializer(serializers.ModelSerializer):
    employement_type_display = serializers.CharField(source="get_employement_type_display", read_only=True)
    experience_level_display = serializers.CharField(source="get_job_type_display", read_only=True)
    job_type_display = serializers.CharField(source="get_job_type_display", read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Job
        fields = ["id", "title", "slug", "description", "company", "skills", "experience", "experience_level", "experience_level_display", "location", "job_type", "job_type_display", "employement_type", "employement_type_display", "views", "applicants", "requirements", "benefits", "salary_range", "posted_date", "expiry_date", "is_expired", "status", "is_active"]
        read_only_fields = ["slug", "posted_date", "views", "applicants"]
        
    def get_is_expired(self, obj):
        """Check if job posting has expired"""
        
        if obj.expiry_date:
            return timezone.now() > obj.expiry_date
        return False



class JobCreateSerializer(serializers.ModelSerializer):
    slug = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = ["title", "slug", "description", "company", "skills", "experience", "experience_level", "location", "job_type", "employement_type", "requirements", "benefits", "salary_range", "expiry_date", "status", "is_active"]
        read_only_fields = ["is_active","slug"]
    
    def validate(self, data):
        """Validate the entire job data"""
        
        expiry_date = data.get("expiry_date")
        
        if expiry_date and expiry_date <= timezone.now():
            raise serializers.ValidationError({
                "expiry_date": "Expiry date must be in the future"
            })
        
        experience = data.get("experience")
        experience_level = data.get("experience_level")
        
        if experience and experience_level:
            pass
        
        return data
    
    def validate_skills(self, value):
        """Validate skills JSON field"""
        
        if not isinstance(value, list):
            raise serializers.ValidationError("Skills Must be a List")
        if len(value) > 20:
            raise serializers.ValidationError("Maximum 20 Skills Allowed")
        return value
    
    def validate_requirements(self, value):
        """Validate requirements JSON field"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Requirements must be a list")
        return value
    
    def validate_benefits(self, value):
        """Validate benefits JSON field"""
        
        if not isinstance(value, list):
            raise serializers.ValidationError("Benefits must be a list")
        return value


class JobUpdateSerializer(serializers.ModelSerializer):
    slug = serializers.ReadOnlyField()
    class Meta:
        model = Job
        fields = [
            "title", "description", "company", "skills", 
            "experience", "location", "job_type", 
            "employement_type", "experience_level", 
            "requirements", "benefits", "salary_range", 
            "expiry_date", "status", "is_active"
        ]
    
    def validate_slug(self, value):
        """Ensure slug isn't changed manually"""
        raise serializers.ValidationError("Slug cannot be modified directly")
        

class EmployerJobListSerializer(serializers.ModelSerializer):
    conversion_rate = serializers.SerializerMethodField()
    days_remainig = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ["id", "title", "slug", "company", "location", "views", "applicants", "job_type", "employement_type", "experience_level", "salary_range", "conversion_rate", "days_remainig", "is_expiring_soon", "posted_date", "status"]
        
    def get_conversion_rate(self, obj):
        """Calculate view to application conversion rate"""
       
        if obj.views > 0:
            return round((obj.applicants / obj.views) * 100, 2)
        return 0
    
    def get_days_remaining(self, obj):
        """Calculate days until expiry"""
        
        if obj.expiry_date:
            delta = obj.expiry_date - timezone.now()
            return max(delta.days, 0)
        return None
    
    def get_is_expiring_soon(self, obj):
        """Check if job expires within 7 days"""
        
        days_remaining = self.get_days_remaining(obj)
        return days_remaining is not None and days_remaining <= 7


class AdminJobSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField()
    last_updated = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = Job
        fields = "__all__"
        # Or explicitly list all fields if you want control
        # fields = [field.name for field in Job._meta.fields]
    
    def get_posted_by(self, obj):
        """Get the user who posted the job (if user model is connected)"""
        # If you have a ForeignKey to User in Job model:
        # return obj.posted_by.username if obj.posted_by else None
        return None  # Update based on your model 


class JobSearchSerializer(serializers.Serializer):
    """Serializer for job search filters"""
    query = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    job_type = serializers.ChoiceField(
        choices=Job.JOB_TYPES, 
        required=False, 
        allow_blank=True
    )
    employement_type = serializers.ChoiceField(
        choices=Job.EMPLOYMENT_TYPES, 
        required=False, 
        allow_blank=True
    )
    experience_level = serializers.ChoiceField(
        choices=Job.EXPERIENCE_LEVELS, 
        required=False, 
        allow_blank=True
    )
    min_experience = serializers.IntegerField(required=False, min_value=0)
    max_experience = serializers.IntegerField(required=False, min_value=0)
    min_salary = serializers.IntegerField(required=False, min_value=0)
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    is_active = serializers.BooleanField(required=False, default=True)


class JobStatsSerializer(serializers.Serializer):
    """Serializer for job statistics"""
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    expired_jobs = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_applicants = serializers.IntegerField()
    avg_views_per_job = serializers.FloatField()
    avg_applicants_per_job = serializers.FloatField()
    jobs_by_type = serializers.DictField()
    jobs_by_location = serializers.DictField()
    recent_jobs = JobListSerializer(many=True)


class JobApplicationCountSerializer(serializers.ModelSerializer):
    """Serializer for job with application count"""
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            "id", "title", "company", "location", 
            "applicants", "application_count", "posted_date"
        ]
    
    def get_application_count(self, obj):
        """Get actual application count if you have Application model"""
        # If you have an Application model:
        # return obj.applications.count()
        return obj.applicants  # Fallback to stored count