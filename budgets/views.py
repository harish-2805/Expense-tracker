from decimal import Decimal
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from .models import Budget
from .forms import BudgetForm
from expenses.models import Expense, Category


@login_required
def budget_list(request):
    user = request.user
    today = date.today()

    # Allow month/year switching via GET params
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    budgets = Budget.objects.filter(user=user, month=month, year=year)
    currency = user.get_currency_symbol()

    budget_data = []
    total_budget = Decimal('0')
    total_spent = Decimal('0')

    for budget in budgets:
        spent = Expense.objects.filter(
            user=user, category=budget.category,
            date__month=month, date__year=year
        ).aggregate(s=Sum('amount'))['s'] or Decimal('0')

        remaining = budget.amount - spent
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0

        if percentage >= 100:
            status = 'danger'
            alert = 'Budget exceeded!'
        elif percentage >= 80:
            status = 'warning'
            alert = 'Close to budget limit!'
        else:
            status = 'success'
            alert = ''

        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': min(percentage, 100),
            'actual_percentage': percentage,
            'status': status,
            'alert': alert,
        })
        total_budget += budget.amount
        total_spent += spent

    # Categories without a budget
    budgeted_categories = budgets.values_list('category', flat=True)
    unbudgeted = [c for c in Category.choices if c[0] not in budgeted_categories]

    context = {
        'budget_data': budget_data,
        'currency': currency,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_remaining': total_budget - total_spent,
        'month': month,
        'year': year,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'unbudgeted': unbudgeted,
        'months': [(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)],
        'years': range(today.year - 2, today.year + 2),
    }
    return render(request, 'budgets/budget_list.html', context)


@login_required
def budget_add(request):
    today = date.today()
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            # Check for duplicate
            existing = Budget.objects.filter(
                user=request.user,
                category=budget.category,
                month=budget.month,
                year=budget.year
            ).first()
            if existing:
                messages.warning(request, f'Budget for {budget.category} in {budget.month}/{budget.year} already exists. Please edit it.')
                return redirect('budget_list')
            budget.save()
            messages.success(request, f'Budget for {budget.category} set to {request.user.get_currency_symbol()}{budget.amount}!')
            return redirect('budget_list')
    else:
        form = BudgetForm(initial={'month': today.month, 'year': today.year})
    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Add', 'currency': request.user.get_currency_symbol()})


@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Edit', 'currency': request.user.get_currency_symbol()})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted.')
        return redirect('budget_list')
    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})
