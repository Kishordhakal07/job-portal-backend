from rest_framework import serializers
from .models import Job, Category


class JobSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        write_only=True
    )
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company_name', 'title', 'description', 'categories',
            'salary_min', 'salary_max', 'currency', 'work_type',
            'due_date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['categories'] = [cat.name for cat in instance.categories.all()]
        return representation

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        company_profile = self.context['request'].user.company_profile

        job = Job.objects.create(company=company_profile, **validated_data)

        category_objects = []
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(name=cat_name.strip())
            category_objects.append(category)
        job.categories.set(category_objects)

        return job

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories_data is not None:
            category_objects = []
            for cat_name in categories_data:
                category, created = Category.objects.get_or_create(name=cat_name.strip())
                category_objects.append(category)
            instance.categories.set(category_objects)

        return instance