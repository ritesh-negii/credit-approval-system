from django.urls import path
from .views import (
    CheckEligibilityView,
    CreateLoanView,
    ViewLoanView,
    ViewLoansByCustomerView,
)


urlpatterns = [
    path("check-eligibility/", CheckEligibilityView.as_view()),
    path("create-loan/", CreateLoanView.as_view()),
    path("view-loan/<int:loan_id>/", ViewLoanView.as_view()),
    path("view-loans/<int:customer_id>/", ViewLoansByCustomerView.as_view()),
]
