from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Customer
from .serializers import CustomerRegisterSerializer


class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data

        # 🔐 Validate required fields
        required_fields = [
            "first_name",
            "last_name",
            "age",
            "monthly_income",
            "phone_number",
        ]

        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            monthly_income = int(data["monthly_income"])
        except ValueError:
            return Response(
                {"error": "monthly_income must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        approved_limit = round((36 * monthly_income) / 100000) * 100000

        customer = Customer.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=int(data["age"]),
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            phone_number=data["phone_number"],
            current_debt=0,
        )

        serializer = CustomerRegisterSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
