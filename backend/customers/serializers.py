from rest_framework import serializers
from .models import Customer


class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "age",
            "monthly_salary",
            "approved_limit",
            "phone_number",
        ]
        read_only_fields = ["id", "approved_limit"]
