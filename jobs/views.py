from rest_framework import generics, permissions
from .models import Job
from .serializers import JobSerializer
from accounts.permissions import IsCompany
from .permissions import IsJobOwner


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_queryset(self):
        return Job.objects.filter(company=self.request.user.company_profile)

    def perform_create(self, serializer):
        serializer.save()


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany, IsJobOwner]
    queryset = Job.objects.all()