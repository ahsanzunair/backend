from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from .paginations import JobPagination
from .models import Job
from .serializers import (
    JobListSerializer, 
    JobDetailSerializer, 
    JobCreateSerializer, 
    JobUpdateSerializer, 
    EmployerJobListSerializer, 
    AdminJobSerializer, 
    JobStatsSerializer
)

# Create your views here.

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(is_active=True)
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    

    filterset_fields = {
        "job_type": ["exact", "in"],
        "employement_type": ["exact", "in"],
        "experience": ["exact", "in"],
        "experience_level": ["exact", "in"],
        "company": ["exact", "icontains"],
        "location": ["exact", "icontains"],
        "status": ["exact"],
        "experience": ["exact", "gte", "lte"],
    }
    
    search_fields = [
        "title", "description", "company", "location", 
        "skills", "requirements"
    ]
    
    ordering_fields = [
        "posted_date", "salary_range", "experience", 
        "views", "applicants"
    ]
    ordering = ["-posted_date"]
    
    def get_queryset(self):
        """Custom queryset based on user and actions"""
        queryset = super().get_queryset()
        
        # Handle different actions
        if self.action == "employer":
            # For employer view, show all jobs (including inactive)
            queryset = Job.objects.all()
            
            # Filter by company if provided
            company = self.request.query_params.get("company", None)
            if company and self.request.user.is_authenticated:
                # You might want to check if user owns this company
                queryset = queryset.filter(company__icontains=company)
                
        elif self.action == "list":
            # Filter out expired jobs for public listing
            queryset = queryset.filter(
                Q(expiry_date__isnull=True) | 
                Q(expiry_date__gt=timezone.now())
            )
            
            # Filter by salary range if provided
            min_salary = self.request.query_params.get("min_salary", None)
            max_salary = self.request.query_params.get("max_salary", None)
            
            # Filter by skills if provided
            skills = self.request.query_params.getlist("skills", [])
            if skills:
                # Assuming skills is a JSONField with list of strings
                for skill in skills:
                    queryset = queryset.filter(skills__contains=[skill])
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == "list":
            return JobListSerializer
        elif self.action == "retrieve":
            return JobDetailSerializer
        elif self.action == "create":
            return JobCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return JobUpdateSerializer
        elif self.action == "employer":
            return EmployerJobListSerializer
        elif self.action in ["stats", "analytics"]:
            return JobStatsSerializer
        return AdminJobSerializer
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.action in ["create", "update", "partial_update", "employer"]:
            return [permissions.IsAuthenticated()]
        elif self.action == "destroy":
            return [permissions.IsAdminUser()]
        elif self.action in ["increment_views", "increment_applicants"]:
            # Allow anyone to increment views
            return [permissions.AllowAny()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        """Set additional fields when creating a job"""
        # You can set the user who created the job if you have a user field
        # serializer.save(posted_by=self.request.user)
        serializer.save()
    
    @action(detail=True, methods=["post"])
    def increment_views(self, request, pk=None):
        """API endpoint to increment job views"""
        job = self.get_object()
        job.views = F("views") + 1
        job.save(update_fields=["views"])
        job.refresh_from_db()
        return Response({"views": job.views})
    
    @action(detail=True, methods=["post"])
    def increment_applicants(self, request, pk=None):
        """API endpoint to increment job applicants count"""
        job = self.get_object()
        job.applicants = F("applicants") + 1
        job.save(update_fields=["applicants"])
        job.refresh_from_db()
        return Response({"applicants": job.applicants})
    
    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured jobs (most viewed, recently posted, etc.)"""
        featured_jobs = self.get_queryset().filter(
            posted_date__gte=timezone.now() - timedelta(days=30)
        ).order_by("-views", "-posted_date")[:10]
        
        serializer = JobListSerializer(featured_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recently posted jobs"""
        recent_jobs = self.get_queryset().order_by("-posted_date")[:20]
        serializer = JobListSerializer(recent_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def urgent(self, request):
        """Get urgent jobs (expiring soon)"""
        urgent_jobs = self.get_queryset().filter(
            expiry_date__isnull=False,
            expiry_date__lte=timezone.now() + timedelta(days=7),
            expiry_date__gt=timezone.now()
        ).order_by("expiry_date")[:10]
        
        serializer = JobListSerializer(urgent_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="employer-jobs")
    def employer(self, request):
        """Get jobs for employer dashboard"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get job statistics"""
        
        # Calculate time ranges
        now = timezone.now()
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        
        # Basic statistics
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(is_active=True).count()
        expired_jobs = Job.objects.filter(
            expiry_date__lt=now,
            is_active=True
        ).count()
        
        # Weekly/Monthly stats
        weekly_jobs = Job.objects.filter(
            posted_date__gte=last_week
        ).count()
        
        monthly_jobs = Job.objects.filter(
            posted_date__gte=last_month
        ).count()
        
        # Aggregated data
        views_data = Job.objects.aggregate(
            total_views=Sum("views"),
            avg_views=Avg("views"),
            max_views=max("views")
        )
        
        applicants_data = Job.objects.aggregate(
            total_applicants=Sum("applicants"),
            avg_applicants=Avg("applicants"),
            max_applicants=max("applicants")
        )
        
        # Distribution by job type
        jobs_by_type = dict(
            Job.objects.values("job_type")
            .annotate(count=Count("id"), total_views=Sum("views"))
            .values_list("job_type", "count")
        )
        
        # Top companies by job count
        top_companies = dict(
            Job.objects.values("company")
            .annotate(job_count=Count("id"))
            .order_by("-job_count")[:10]
            .values_list("company", "job_count")
        )
        
        # Top locations
        top_locations = dict(
            Job.objects.values("location")
            .annotate(job_count=Count("id"))
            .order_by("-job_count")[:10]
            .values_list("location", "job_count")
        )
        
        # Recent jobs for the stats
        recent_jobs = Job.objects.filter(
            posted_date__gte=last_month
        ).order_by("-posted_date")[:5]
        
        stats_data = {
            "overview": {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "expired_jobs": expired_jobs,
                "weekly_new_jobs": weekly_jobs,
                "monthly_new_jobs": monthly_jobs,
            },
            "performance": {
                "total_views": views_data["total_views"] or 0,
                "avg_views_per_job": round(views_data["avg_views"] or 0, 2),
                "max_views": views_data["max_views"] or 0,
                "total_applicants": applicants_data["total_applicants"] or 0,
                "avg_applicants_per_job": round(applicants_data["avg_applicants"] or 0, 2),
                "max_applicants": applicants_data["max_applicants"] or 0,
                "conversion_rate": round(
                    (applicants_data["total_applicants"] or 0) / 
                    (views_data["total_views"] or 1) * 100, 
                    2
                ) if views_data["total_views"] else 0,
            },
            "distribution": {
                "jobs_by_type": jobs_by_type,
                "jobs_by_employment_type": dict(
                    Job.objects.values("employement_type")
                    .annotate(count=Count("id"))
                    .values_list("employement_type", "count")
                ),
                "jobs_by_experience_level": dict(
                    Job.objects.values("experience_level")
                    .annotate(count=Count("id"))
                    .values_list("experience_level", "count")
                ),
            },
            "top_lists": {
                "top_companies": top_companies,
                "top_locations": top_locations,
                "most_viewed_jobs": JobListSerializer(
                    Job.objects.order_by("-views")[:5], 
                    many=True
                ).data,
                "most_applied_jobs": JobListSerializer(
                    Job.objects.order_by("-applicants")[:5], 
                    many=True
                ).data,
            },
            "recent_activity": {
                "recent_jobs": JobListSerializer(recent_jobs, many=True).data,
                "recent_expired_jobs": Job.objects.filter(
                    expiry_date__gte=last_week,
                    expiry_date__lt=now
                ).count(),
            }
        }
        
        serializer = JobStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get detailed analytics for admin/employer"""
        if not request.user.is_staff and not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Time-based analytics
        now = timezone.now()
        date_ranges = {
            "today": now - timedelta(days=1),
            "week": now - timedelta(days=7),
            "month": now - timedelta(days=30),
            "quarter": now - timedelta(days=90),
            "year": now - timedelta(days=365),
        }
        
        analytics_data = {}
        
        for period, start_date in date_ranges.items():
            period_jobs = Job.objects.filter(posted_date__gte=start_date)
            
            analytics_data[period] = {
                "jobs_posted": period_jobs.count(),
                "jobs_active": period_jobs.filter(is_active=True).count(),
                "total_views": period_jobs.aggregate(Sum("views"))["views__sum"] or 0,
                "total_applicants": period_jobs.aggregate(Sum("applicants"))["applicants__sum"] or 0,
                "avg_views_per_job": period_jobs.aggregate(Avg("views"))["views__avg"] or 0,
                "avg_applicants_per_job": period_jobs.aggregate(Avg("applicants"))["applicants__avg"] or 0,
            }
        
        return Response(analytics_data)
    
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a job (soft delete)"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        job = self.get_object()
        
        # Check if user has permission to deactivate
        # You might want to add ownership check here
        # if job.posted_by != request.user and not request.user.is_staff:
        #     return Response(...)
        
        job.is_active = False
        job.save()
        return Response({"status": "Job deactivated successfully"})
    
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a deactivated job"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        job = self.get_object()
        
        # Check if job is expired
        if job.expiry_date and job.expiry_date < timezone.now():
            return Response(
                {"detail": "Cannot activate expired job"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.is_active = True
        job.save()
        return Response({"status": "Job activated successfully"})
    
    @action(detail=False, methods=["get"])
    def search_suggestions(self, request):
        """Get search suggestions for autocomplete"""
        query = request.query_params.get("q", "").strip()
        
        if not query or len(query) < 2:
            return Response({"suggestions": []})
        
        # Job titles suggestions
        title_suggestions = Job.objects.filter(
            title__icontains=query,
            is_active=True
        ).values_list("title", flat=True).distinct()[:10]
        
        # Company suggestions
        company_suggestions = Job.objects.filter(
            company__icontains=query,
            is_active=True
        ).values_list("company", flat=True).distinct()[:10]
        
        # Location suggestions
        location_suggestions = Job.objects.filter(
            location__icontains=query,
            is_active=True
        ).values_list("location", flat=True).distinct()[:10]
        
        # Skill suggestions (assuming skills is a JSON list field)
        skill_suggestions = []
        all_skills = Job.objects.filter(is_active=True).values_list("skills", flat=True)
        
        # Flatten and filter skills
        flattened_skills = set()
        for skill_list in all_skills:
            if skill_list:
                for skill in skill_list:
                    if query.lower() in skill.lower():
                        flattened_skills.add(skill)
        
        skill_suggestions = list(flattened_skills)[:10]
        
        return Response({
            "titles": list(title_suggestions),
            "companies": list(company_suggestions),
            "locations": list(location_suggestions),
            "skills": list(skill_suggestions),
        })