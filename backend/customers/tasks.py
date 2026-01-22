import pandas as pd
from celery import shared_task
from .models import Customer


@shared_task
def ingest_customers_from_excel():
    df = pd.read_excel(
        "/app/data/customer_data.xlsx",
        engine="openpyxl"
    )
    df.columns = df.columns.str.strip().str.lower()

    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            id=row["customer_id"],
            defaults={
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "phone_number": str(row["phone_number"]),
                "monthly_salary": int(row["monthly_salary"]),
                "approved_limit": int(row["approved_limit"]),
                "current_debt": int(row["current_debt"]),
                "age": 30,
            }
        )

    return "Customer data ingested successfully"

