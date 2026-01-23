from datetime import date
import math

from loans.models import Loan


def calculate_credit_score(customer):
    score = 100
    loans = Loan.objects.filter(customer=customer)

    for loan in loans:
        # late EMIs
        score -= (loan.tenure - loan.emis_paid_on_time) * 5

        # number of loans
        score -= 2

        # loan activity in current year
        if loan.start_date.year == date.today().year:
            score -= 5

    return max(score, 0)


def calculate_emi(principal, annual_rate, tenure):
    r = annual_rate / (12 * 100)
    return (principal * r * math.pow(1 + r, tenure)) / (
        math.pow(1 + r, tenure) - 1
    )

