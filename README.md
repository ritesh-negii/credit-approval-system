# Credit Approval System (Backend)

This project is a backend-only Credit Approval System developed as part of a Backend Internship Assignment.  
The system evaluates customer loan eligibility based on historical loan data and predefined credit rules.

The application is built using Django, Django Rest Framework, PostgreSQL, Docker, and Celery, and exposes REST APIs for customer registration and loan management.

---

## Tech Stack

- Python 3.11
- Django 4+
- Django Rest Framework
- PostgreSQL
- Docker & Docker Compose
- Celery + Redis
- Pandas (for Excel data ingestion)

---

## Project Overview

The Credit Approval System provides REST APIs to:

- Register new customers
- Check loan eligibility using a credit score
- Create loans for eligible customers
- View individual loan details
- View all loans for a customer
- Ingest historical customer and loan data using background workers

There is **no frontend**, as required by the assignment.  
All APIs are tested using Postman.

---

## Data Models

### Customer
- `first_name`
- `last_name`
- `age`
- `phone_number` (unique)
- `monthly_salary`
- `approved_limit`
- `current_debt`

### Loan
- `customer` (Foreign Key → Customer)
- `loan_amount`
- `tenure`
- `interest_rate`
- `monthly_installment`
- `emis_paid_on_time`
- `start_date`
- `end_date`

---

## Credit Score Logic

Each customer is assigned a **credit score out of 100**, calculated using:

- Past EMIs paid on time
- Number of loans taken
- Loan activity in the current year
- Total loan volume

### Business Rules

- If total loan amount exceeds approved limit → credit score = 0
- If total EMI exceeds 50% of monthly salary → loan rejected

### Loan Approval Rules

- Credit score > 50 → loan approved
- 30 < score ≤ 50 → loan approved with interest rate ≥ 12%
- 10 < score ≤ 30 → loan approved with interest rate ≥ 16%
- score ≤ 10 → loan rejected

If the requested interest rate does not match the slab, it is automatically corrected.

---

## EMI Calculation

Monthly EMI is calculated using a compound interest scheme.

---

## API Endpoints

### Register Customer
`POST /api/customers/register/`

Registers a new customer and calculates approved credit limit.

---

### Check Loan Eligibility
`POST /api/loans/check-eligibility/`

Checks whether a customer is eligible for a loan based on credit score and rules.

---

### Create Loan
`POST /api/loans/create-loan/`

Creates a loan for an eligible customer and stores it in the database.

---

### View Loan by Loan ID
`GET /api/loans/view-loan/<loan_id>/`

Returns loan details along with customer information.

---

### View Loans by Customer ID
`GET /api/loans/view-loans/<customer_id>/`

Returns all loans associated with a specific customer.

---

## Background Data Ingestion

- Customer and loan data are ingested from Excel files:
  - `customer_data.xlsx`
  - `loan_data.xlsx`
- Ingestion is handled asynchronously using **Celery background workers**

---

## Running the Project

### Prerequisites
- Docker
- Docker Compose

### Start the application
```bash
docker compose up --build
