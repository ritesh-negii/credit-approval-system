import pandas as pd
from celery import shared_task
from customers.models import Customer
from .models import Loan


@shared_task
def ingest_loans_from_excel():
    df = pd.read_excel(
        "/app/data/loan_data.xlsx",
        engine="openpyxl"
    )

    
    df.columns = df.columns.str.strip().str.lower()

    for _, row in df.iterrows():
        customer = Customer.objects.get(id=row["customer id"])

        Loan.objects.update_or_create(
            id=row["loan id"],
            defaults={
                "customer": customer,
                "loan_amount": float(row["loan amount"]),
                "tenure": int(row["tenure"]),
                "interest_rate": float(row["interest rate"]),
                "monthly_installment": float(row["monthly repayment (emi)"]),
                "emis_paid_on_time": int(row["emis paid on time"]),
                "start_date": row["start date"],
                "end_date": row["end date"],
            }
        )

    return "Loan data ingested successfully"
