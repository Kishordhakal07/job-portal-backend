from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsCompany
from .filters import JobFilter
from .models import Job
from .permissions import IsJobOwner
from .serializers import JobSerializer


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_queryset(self):
        return Job.objects.filter(
            company=self.request.user.company_profile
        ).order_by('-created_at')


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany, IsJobOwner]
    queryset = Job.objects.all()


class JobArchiveView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompany, IsJobOwner]

    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        self.check_object_permissions(request, job)

        if job.status == Job.Status.ARCHIVED:
            return Response({'detail': 'Job is already archived.'}, status=400)

        job.status = Job.Status.ARCHIVED
        job.save(update_fields=['status', 'updated_at'])

        serializer = JobSerializer(job, context={'request': request})
        return Response(serializer.data)


class PublicJobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'company__company_name', 'categories__name']
    ordering_fields = ['created_at', 'due_date', 'salary_max']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Job.objects
            .filter(status=Job.Status.ACTIVE, due_date__gte=timezone.localdate())
            .select_related('company')
            .prefetch_related('categories')
        )