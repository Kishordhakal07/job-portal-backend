import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='categories__name', lookup_expr='iexact')
    min_salary = django_filters.NumberFilter(field_name='salary_max', lookup_expr='gte')

    class Meta:
        model = Job
        fields = ['work_type', 'currency']