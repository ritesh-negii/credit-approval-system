from django.urls import path
from .views import CheckEligibilityView

urlpatterns = [
    path("check-eligibility/", CheckEligibilityView.as_view()),
]
