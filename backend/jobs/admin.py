from django.contrib import admin
from .models import Job

# Register your models here.


class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "logo", "slug", "location", "views", "applicants", "is_active")
    search_fields = ("title", "company")
    list_filter = ("location",)
    ordering = ("posted_date",)

admin.site.register(Job, JobAdmin)