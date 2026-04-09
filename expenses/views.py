import csv
import json
from datetime import date, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth, TruncDate
from django.http import HttpResponse
from django.utils import timezone

from .models import Expense, Category
from .forms import ExpenseForm
from budgets.models import Budget
from shared_expenses.models import SharedExpense, Participant


@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    current_month = today.month
    current_year = today.year
    first_of_month = today.replace(day=1)
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

    # Recent transactions
    recent_personal = list(Expense.objects.filter(user=user).order_by('-date', '-created_at')[:5])
    recent_shared_ids = user_participations.values_list('shared_expense_id', flat=True)
    recent_shared = list(SharedExpense.objects.filter(id__in=recent_shared_ids).order_by('-date', '-created_at')[:5])

    all_recent = []
    for e in recent_personal:
        all_recent.append({
            'type': 'personal', 'title': e.title, 'amount': e.amount,
            'date': e.date, 'category': e.category, 'id': e.id
        })
    for se in recent_shared:
        part = user_participations.filter(shared_expense=se).first()
        all_recent.append({
            'type': 'shared', 'title': se.title,
            'amount': part.share_amount if part else se.total_amount,
            'date': se.date, 'category': 'Shared', 'id': se.id
        })
    all_recent.sort(key=lambda x: x['date'], reverse=True)
    all_recent = all_recent[:5]

    insights = generate_insights(user, category_spending, total_monthly, total_budget, remaining_budget)

    # ── CHART 1: Pie – category split current month ───────────────────────────
    cat_data = {row['category']: float(row['total'])
                for row in monthly_expenses.values('category').annotate(total=Sum('amount'))}
    shared_paid_total = float(
        Participant.objects.filter(user=user, is_payer=True, shared_expense__date__gte=first_of_month)
        .aggregate(s=Sum('share_amount'))['s'] or 0
    )
    if shared_paid_total > 0:
        cat_data['Shared (Paid)'] = cat_data.get('Shared (Paid)', 0) + shared_paid_total
    pie_labels = list(cat_data.keys())
    pie_values = [round(v, 2) for v in cat_data.values()]

    # ── CHART 2: Bar – monthly totals last 6 months ───────────────────────────
    six_months_ago = (today.replace(day=1) - timedelta(days=150)).replace(day=1)
    personal_monthly = (
        Expense.objects.filter(user=user, date__gte=six_months_ago)
        .annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount'))
    )
    shared_monthly = (
        Participant.objects.filter(user=user, is_payer=True, shared_expense__date__gte=six_months_ago)
        .annotate(month=TruncMonth('shared_expense__date')).values('month').annotate(total=Sum('share_amount'))
    )
    bar_buckets = {}
    for row in personal_monthly:
        key = row['month'].strftime('%b %Y')
        bar_buckets[key] = bar_buckets.get(key, 0) + float(row['total'])
    for row in shared_monthly:
        key = row['month'].strftime('%b %Y')
        bar_buckets[key] = bar_buckets.get(key, 0) + float(row['total'])
    bar_labels, bar_values = [], []
    for i in range(5, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        label = month_date.strftime('%b %Y')
        bar_labels.append(label)
        bar_values.append(round(bar_buckets.get(label, 0), 2))

    # ── CHART 3: Line – daily spending current month ──────────────────────────
    daily_personal = (
        Expense.objects.filter(user=user, date__gte=first_of_month)
        .annotate(day=TruncDate('date')).values('day').annotate(total=Sum('amount'))
    )
    daily_shared = (
        Participant.objects.filter(user=user, is_payer=True, shared_expense__date__gte=first_of_month)
        .annotate(day=TruncDate('shared_expense__date')).values('day').annotate(total=Sum('share_amount'))
    )
    daily_buckets = {}
    for row in daily_personal:
        key = row['day'].strftime('%d %b')
        daily_buckets[key] = daily_buckets.get(key, 0) + float(row['total'])
    for row in daily_shared:
        key = row['day'].strftime('%d %b')
        daily_buckets[key] = daily_buckets.get(key, 0) + float(row['total'])
    line_labels, line_values = [], []
    day_cursor = first_of_month
    while day_cursor <= today:
        label = day_cursor.strftime('%d %b')
        line_labels.append(label)
        line_values.append(round(daily_buckets.get(label, 0), 2))
        day_cursor += timedelta(days=1)

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
        'pie_labels': json.dumps(pie_labels),
        'pie_values': json.dumps(pie_values),
        'bar_labels': json.dumps(bar_labels),
        'bar_values': json.dumps(bar_values),
        'line_labels': json.dumps(line_labels),
        'line_values': json.dumps(line_values),
    }
    return render(request, 'expenses/dashboard.html', context)


def generate_insights(user, category_spending, total_monthly, total_budget, remaining_budget):
    insights = []
    if not category_spending:
        insights.append({'type': 'info', 'icon': 'bi-info-circle',
                         'message': 'Start adding expenses to see insights here.'})
        return insights
    if category_spending:
        top_cat = max(category_spending, key=category_spending.get)
        top_amt = category_spending[top_cat]
        if top_cat in ['Shopping', 'Entertainment'] and total_monthly > 0:
            pct = (top_amt / total_monthly) * 100
            if pct > 40:
                insights.append({'type': 'warning', 'icon': 'bi-exclamation-triangle',
                                  'message': f'You are spending a lot on {top_cat} ({pct:.0f}% of total). Consider reducing it.'})
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
    food_amt = category_spending.get('Food', Decimal('0'))
    if total_monthly > 0 and food_amt / total_monthly > Decimal('0.5'):
        insights.append({'type': 'warning', 'icon': 'bi-cup-hot',
                          'message': 'More than 50% of your spending is on Food. Try cooking at home more often.'})
    return insights


@login_required
def expense_list(request):
    user = request.user
    expenses = Expense.objects.filter(user=user)
    search_query = request.GET.get('q', '')
    if search_query:
        expenses = expenses.filter(Q(title__icontains=search_query) | Q(notes__icontains=search_query))
    category_filter = request.GET.get('category', '')
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj, 'total': total,
        'search_query': search_query, 'category_filter': category_filter,
        'categories': Category.choices, 'currency': user.get_currency_symbol(),
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
    return render(request, 'expenses/expense_form.html',
                  {'form': form, 'action': 'Add', 'currency': request.user.get_currency_symbol()})


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
    return render(request, 'expenses/expense_form.html',
                  {'form': form, 'action': 'Edit', 'expense': expense, 'currency': request.user.get_currency_symbol()})


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
    return render(request, 'expenses/expense_detail.html',
                  {'expense': expense, 'currency': request.user.get_currency_symbol()})


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Payment Method', 'Date', 'Notes'])
    expenses = Expense.objects.filter(user=request.user)
    category_filter = request.GET.get('category', '')
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    for expense in expenses:
        writer.writerow([expense.title, expense.amount, expense.category,
                         expense.payment_method, expense.date, expense.notes or ''])
    return response