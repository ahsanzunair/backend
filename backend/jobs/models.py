from django.db import models
from django.utils.text import slugify
from users.models import User

# Create your models here.


class Job(models.Model):
    EMPLOYMENT_TYPES = [
        ("full_time", "Full_Time"),
        ("part_time", "Part_Time"),
        ("internship", "Internship"),
        ("freelance", "Freelance"),
        ("contract", "Contract"),
        ("permanent", "Permanent"),
        ("temporary", "Temporary"),
    ]
    
    EXPERIENCE_LEVELS = [
        ("fresher", "Fresher"),
        ("entry_level", "Entry_level"),
        ("junior", "Junior"),
        ("mid", "Mid"),
        ("senior", "Senior"),
        ("lead", "Lead"),
        ("manager", "Manager"),
        ("director", "Director"),
        ("executive", "Executive"),
    ]
    
    JOB_TYPES = [
        ("onsite", "Onsite"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]
    
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]
    
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs", default=1)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    logo = models.ImageField(blank=True, null=True)
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
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="draft")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.company}")
        super().save(*args, **kwargs)



class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "job")