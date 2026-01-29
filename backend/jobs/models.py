from django.db import models
from django.utils.text import slugify

# Create your models here.


class Job(models.Model):
    EMPLOYMENT_TYPES = [
        ("full_time", "Full_Time"),
        ("part_time", "Part_Time"),
        ("internship", "Internship"),
        ("contract", "Contract"),
    ]
    
    EXPERIENCE_LEVELS = [
        ("fresher", "Fresher"),
        ("junior", "Junior"),
        ("mid", "Mid"),
        ("senior", "Senior"),
        ("lead", "Lead"),
    ]
    
    JOB_TYPES = [
        ("onsite", "Onsite"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    employement_type = models.CharField(max_length=25, choices=EMPLOYMENT_TYPES, default="full_time")
    salary_range = models.CharField(max_length=50, blank=True, null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    applicants = models.IntegerField(default=0)
    expiry_date = models.DateTimeField(blank=True, null=True)
    skills = models.JSONField(default=list)
    experience = models.IntegerField(default=0)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    requirements = models.JSONField(default=list, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.company}")
        super().save(*args, **kwargs)