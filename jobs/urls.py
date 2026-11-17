from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    JobArchiveView,
    PublicJobListView,
)

urlpatterns = [
    path('', JobListCreateView.as_view(), name='job-list-create'),
    path('public/', PublicJobListView.as_view(), name='job-public-list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('<int:pk>/archive/', JobArchiveView.as_view(), name='job-archive'),
]