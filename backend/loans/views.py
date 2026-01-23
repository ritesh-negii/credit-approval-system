from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from customers.models import Customer
from loans.models import Loan
from loans.serializers import CheckEligibilitySerializer
from loans.services import calculate_credit_score, calculate_emi
from datetime import date, timedelta


class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        customer = Customer.objects.get(id=data["customer_id"])

        loans = Loan.objects.filter(customer=customer)

        # Rule 1: total loan amount > approved limit
        total_loan_amount = sum(loan.loan_amount for loan in loans)
        if total_loan_amount > customer.approved_limit:
            return Response(
                {
                    "customer_id": customer.id,
                    "approval": False,
                    "credit_score": 0,
                    "message": "Loan limit exceeded",
                },
                status=status.HTTP_200_OK,
            )

        # Rule 2: total EMI > 50% salary
        total_emi = sum(loan.monthly_installment for loan in loans)
        if total_emi > 0.5 * customer.monthly_salary:
            return Response(
                {
                    "customer_id": customer.id,
                    "approval": False,
                    "message": "EMI exceeds 50% of salary",
                },
                status=status.HTTP_200_OK,
            )

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

        monthly_installment = calculate_emi(
            data["loan_amount"],
            corrected_interest_rate,
            data["tenure"],
        )

        return Response(
            {
                "customer_id": customer.id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": corrected_interest_rate,
                "tenure": data["tenure"],
                "monthly_installment": round(monthly_installment, 2),
            },
            status=status.HTTP_200_OK,
        )


class CreateLoanView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        customer = Customer.objects.get(id=data["customer_id"])

        credit_score = calculate_credit_score(customer)

        interest_rate = data["interest_rate"]
        approval = False

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            interest_rate = max(interest_rate, 12)
            approval = True
        elif 10 < credit_score <= 30:
            interest_rate = max(interest_rate, 16)
            approval = True

        if not approval:
            return Response(
                {
                    "loan_id": None,
                    "customer_id": customer.id,
                    "loan_approved": False,
                    "message": "Credit score too low",
                },
                status=status.HTTP_200_OK,
            )

        monthly_installment = calculate_emi(
            data["loan_amount"],
            interest_rate,
            data["tenure"],
        )

        start_date = date.today()
        end_date = start_date + timedelta(days=30 * data["tenure"])

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=data["loan_amount"],
            tenure=data["tenure"],
            interest_rate=interest_rate,
            monthly_installment=monthly_installment,
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date,
        )

        return Response(
            {
                "loan_id": loan.id,
                "customer_id": customer.id,
                "loan_approved": True,
                "message": "Loan approved",
                "monthly_installment": round(monthly_installment, 2),
            },
            status=status.HTTP_201_CREATED,
        )

class ViewLoanView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {"error": "Loan not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        customer = loan.customer

        return Response({
            "loan_id": loan.id,
            "customer": {
                "id": customer.id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age,
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure,
        })

class ViewLoansByCustomerView(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer_id=customer_id)

        if not loans.exists():
            return Response(
                {"message": "No loans found for this customer"},
                status=status.HTTP_404_NOT_FOUND
            )

        response = []
        for loan in loans:
            response.append({
                "loan_id": loan.id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "repayments_left": loan.tenure - loan.emis_paid_on_time,
            })

        return Response(response)
