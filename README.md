
# 💰 Personal Expense Tracker with Friends & Shared Expenses

A full-stack Django web application for tracking personal and shared expenses, managing budgets, and getting spending insights. Users can add friends to share expenses, split bills, and track payments.

## Features

- User Authentication — Register/Login  
- Expense Management — Add, edit, delete, filter, search, paginate  
- Budget Management — Set monthly budgets with alerts  
- Dashboard — Summary cards, category-wise spending, insights  
- Friends & Shared Expenses — Send friend requests; share bills only with friends  
- Settlement System — Partial payments, UPI simulation, history  
- Export CSV — Download expenses  

## Setup

1. Install Python 3.10+ and PostgreSQL  
2. Create database `expense_tracker_db` and user  
3. Clone the project and create virtual environment  
4. Copy `.env.example` → `.env` and fill in DB credentials  
5. Install dependencies: `pip install -r requirements.txt`  
6. Run migrations: `python manage.py migrate`  
7. (Optional) Load sample data: `python manage.py load_sample_data`  
8. Create superuser: `python manage.py createsuperuser`  
9. Run server: `python manage.py runserver`  

## Project Structure
expense_tracker/
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── expense_tracker/
├── accounts/
├── expenses/
├── budgets/
├── shared_expenses/
└── templates/

## Pages

- `/` — Redirects to Dashboard  
- `/accounts/register/` — Register  
- `/accounts/login/` — Login  
- `/dashboard/` — Main Dashboard  
- `/dashboard/expenses/` — Expense List  
- `/dashboard/expenses/add/` — Add Expense  
- `/budgets/` — Budget Management  
- `/shared/` — Shared Expenses (with friends)  
- `/admin/` — Django Admin  

## Notes

- Only accepted friends appear in shared expenses  
- UPI Pay simulates payments (no real money)  
- Export CSV to download expenses  
