import csv
from datetime import date
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.utils import timezone

from .models import Expense, Category
from .forms import ExpenseForm
from budgets.models import Budget
from shared_expenses.models import SharedExpense, Participant


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    current_month = today.month
    current_year = today.year
    currency = user.get_currency_symbol()

    # Personal expenses this month
    monthly_expenses = Expense.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    )
    total_monthly = monthly_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Category-wise spending
    category_spending = {}
    for cat in Category:
        total = monthly_expenses.filter(category=cat).aggregate(s=Sum('amount'))['s'] or Decimal('0')
        if total > 0:
            category_spending[cat] = total

    # Highest spending category
    highest_category = max(category_spending, key=category_spending.get) if category_spending else None

    # Budget summary
    budgets = Budget.objects.filter(user=user, month=current_month, year=current_year)
    total_budget = budgets.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    remaining_budget = total_budget - total_monthly

    # Budget alerts
    budget_alerts = []
    for budget in budgets:
        spent = monthly_expenses.filter(category=budget.category).aggregate(s=Sum('amount'))['s'] or Decimal('0')
        if budget.amount > 0:
            pct = (spent / budget.amount) * 100
            if pct >= 100:
                budget_alerts.append({'type': 'danger', 'category': budget.category,
                                       'message': f'Budget exceeded for {budget.category}!'})
            elif pct >= 80:
                budget_alerts.append({'type': 'warning', 'category': budget.category,
                                       'message': f'Approaching limit for {budget.category} ({pct:.0f}% used)'})

    # Shared expenses
    user_participations = Participant.objects.filter(user=user)
    shared_total = user_participations.aggregate(s=Sum('share_amount'))['s'] or Decimal('0')

    # Recent 5 transactions (personal + shared)
    recent_personal = list(Expense.objects.filter(user=user).order_by('-date', '-created_at')[:5])
    recent_shared_ids = user_participations.values_list('shared_expense_id', flat=True)
    recent_shared = list(SharedExpense.objects.filter(id__in=recent_shared_ids).order_by('-date', '-created_at')[:5])

    # Merge and sort recent transactions
    all_recent = []
    for e in recent_personal:
        all_recent.append({
            'type': 'personal', 'title': e.title, 'amount': e.amount,
            'date': e.date, 'category': e.category, 'id': e.id
        })
    for se in recent_shared:
        part = user_participations.filter(shared_expense=se).first()
        all_recent.append({
            'type': 'shared', 'title': se.title, 'amount': part.share_amount if part else se.total_amount,
            'date': se.date, 'category': 'Shared', 'id': se.id
        })
    all_recent.sort(key=lambda x: x['date'], reverse=True)
    all_recent = all_recent[:5]

    # Insights
    insights = generate_insights(user, category_spending, total_monthly, total_budget, remaining_budget)

    context = {
        'currency': currency,
        'total_monthly': total_monthly,
        'shared_total': shared_total,
        'total_budget': total_budget,
        'remaining_budget': remaining_budget,
        'category_spending': category_spending,
        'highest_category': highest_category,
        'all_recent': all_recent,
        'budget_alerts': budget_alerts,
        'insights': insights,
        'current_month_name': today.strftime('%B %Y'),
    }
    return render(request, 'expenses/dashboard.html', context)


def generate_insights(user, category_spending, total_monthly, total_budget, remaining_budget):
    """Generate spending insights and suggestions."""
    insights = []
    if not category_spending:
        insights.append({'type': 'info', 'icon': 'bi-info-circle',
                         'message': 'Start adding expenses to see insights here.'})
        return insights

    # Highest category warning
    if category_spending:
        top_cat = max(category_spending, key=category_spending.get)
        top_amt = category_spending[top_cat]
        if top_cat in ['Shopping', 'Entertainment'] and total_monthly > 0:
            pct = (top_amt / total_monthly) * 100
            if pct > 40:
                insights.append({'type': 'warning', 'icon': 'bi-exclamation-triangle',
                                  'message': f'You are spending a lot on {top_cat} ({pct:.0f}% of total). Consider reducing it.'})

    # Budget status
    if total_budget > 0:
        if remaining_budget < 0:
            insights.append({'type': 'danger', 'icon': 'bi-x-circle',
                              'message': f'You have exceeded your total monthly budget! Overspent by ₹{abs(remaining_budget):,.2f}.'})
        elif remaining_budget < total_budget * Decimal('0.2'):
            insights.append({'type': 'warning', 'icon': 'bi-exclamation-circle',
                              'message': 'Only 20% of your monthly budget remains. Spend wisely!'})
        else:
            insights.append({'type': 'success', 'icon': 'bi-check-circle',
                              'message': 'Great job! You are well within your monthly budget.'})
    else:
        insights.append({'type': 'info', 'icon': 'bi-piggy-bank',
                          'message': 'No budget set for this month. Set budgets to track your spending goals.'})

    # Food spending
    food_amt = category_spending.get('Food', Decimal('0'))
    if total_monthly > 0 and food_amt / total_monthly > Decimal('0.5'):
        insights.append({'type': 'warning', 'icon': 'bi-cup-hot',
                          'message': 'More than 50% of your spending is on Food. Try cooking at home more often.'})

    return insights


# ──────────────────────────────────────────────────────────────────────────────
# EXPENSE CRUD
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def expense_list(request):
    user = request.user
    expenses = Expense.objects.filter(user=user)

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        expenses = expenses.filter(Q(title__icontains=search_query) | Q(notes__icontains=search_query))

    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        expenses = expenses.filter(category=category_filter)

    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Pagination
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total': total,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': Category.choices,
        'currency': user.get_currency_symbol(),
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f'Expense "{expense.title}" added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(initial={'date': date.today()})
    return render(request, 'expenses/expense_form.html', {'form': form, 'action': 'Add', 'currency': request.user.get_currency_symbol()})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, f'Expense "{expense.title}" updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'action': 'Edit', 'expense': expense, 'currency': request.user.get_currency_symbol()})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{title}" deleted.')
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'expenses/expense_detail.html', {'expense': expense, 'currency': request.user.get_currency_symbol()})


@login_required
def export_csv(request):
    """Export user's expenses as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Payment Method', 'Date', 'Notes'])

    expenses = Expense.objects.filter(user=request.user)
    category_filter = request.GET.get('category', '')
    if category_filter:
        expenses = expenses.filter(category=category_filter)

    for expense in expenses:
        writer.writerow([
            expense.title, expense.amount, expense.category,
            expense.payment_method, expense.date, expense.notes or ''
        ])

    return response
