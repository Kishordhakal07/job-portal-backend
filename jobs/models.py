from django.db import models
from django.conf import settings
from accounts.models import CompanyProfile


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    class WorkType(models.TextChoices):
        WFH = 'wfh', 'Work From Home'
        WFO = 'wfo', 'Work From Office'
        HYBRID = 'hybrid', 'Hybrid'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    class Currency(models.TextChoices):
        USD = 'usd', 'USD'
        NPR = 'npr', 'NPR'
        EUR = 'eur', 'EUR'
        INR = 'inr', 'INR'

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='jobs', blank=True)

    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, choices=Currency.choices, null=True, blank=True)

    work_type = models.CharField(max_length=10, choices=WorkType.choices)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"