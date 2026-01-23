from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import IntegrityError

from .models import Customer


class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data

        # 1️⃣ Required fields check
        required_fields = [
            "first_name",
            "last_name",
            "age",
            "monthly_income",
            "phone_number",
        ]

        for field in required_fields:
            if field not in data or data[field] in [None, ""]:
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 2️⃣ Type validation
        try:
            age = int(data["age"])
            monthly_income = int(data["monthly_income"])
            phone_number = str(data["phone_number"])
        except ValueError:
            return Response(
                {"error": "age and monthly_income must be numbers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3️⃣ Approved limit logic (assignment rule)
        # approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        approved_limit = round((36 * monthly_income) / 100000) * 100000

        # 4️⃣ Create customer safely (handle duplicate phone number)
        try:
            customer = Customer.objects.create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                age=age,
                monthly_salary=monthly_income,
                approved_limit=approved_limit,
                phone_number=phone_number,
                current_debt=0,
            )
        except IntegrityError:
            return Response(
                {"error": "Customer with this phone number already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5️⃣ Success response
        return Response(
            {
                "customer_id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": customer.monthly_salary,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number,
            },
            status=status.HTTP_201_CREATED,
        )
