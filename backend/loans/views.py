from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from customers.models import Customer
from loans.models import Loan
from loans.services import calculate_credit_score
from loans.serializers import CheckEligibilitySerializer

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        customer = Customer.objects.get(id=data["customer_id"])

        # Rule 1: current loans > approved limit
        total_loan_amount = sum(
            loan.loan_amount for loan in Loan.objects.filter(customer=customer)
        )

        if total_loan_amount > customer.approved_limit:
            return Response({
                "customer_id": customer.id,
                "approval": False,
                "credit_score": 0,
                "message": "Loan limit exceeded"
            })

        # Rule 2: EMI > 50% salary
        total_emi = sum(
            loan.monthly_installment for loan in Loan.objects.filter(customer=customer)
        )

        if total_emi > 0.5 * customer.monthly_salary:
            return Response({
                "customer_id": customer.id,
                "approval": False,
                "message": "EMI exceeds 50% of salary"
            })

        credit_score = calculate_credit_score(customer)

        interest_rate = data["interest_rate"]
        corrected_interest_rate = interest_rate
        approval = False

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            corrected_interest_rate = max(interest_rate, 12)
            approval = True
        elif 10 < credit_score <= 30:
            corrected_interest_rate = max(interest_rate, 16)
            approval = True

        return Response({
            "customer_id": customer.id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": data["tenure"],
            "monthly_installment": (
                data["loan_amount"] / data["tenure"]
            )
        })
