from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import SharedExpense, Participant, Settlement
from .forms import SharedExpenseForm, SettlementForm
from accounts.models import CustomUser


@login_required
def shared_expense_list(request):
    user = request.user
    # Expenses created by user OR user is a participant
    my_participations = Participant.objects.filter(user=user).values_list('shared_expense_id', flat=True)
    shared_expenses = SharedExpense.objects.filter(
        id__in=list(my_participations)
    ).distinct().order_by('-date', '-created_at')

    # Annotate with user's info
    expense_data = []
    for se in shared_expenses:
        participant = Participant.objects.filter(shared_expense=se, user=user).first()
        expense_data.append({
            'expense': se,
            'my_share': participant.share_amount if participant else Decimal('0'),
            'amount_due': participant.amount_due() if participant else Decimal('0'),
            'is_payer': participant.is_payer if participant else False,
            'is_settled': participant.is_settled if participant else False,
        })

    context = {
        'expense_data': expense_data,
        'currency': user.get_currency_symbol(),
    }
    return render(request, 'shared_expenses/shared_list.html', context)


@login_required
def shared_expense_create(request):
    user = request.user
    if request.method == 'POST':
        form = SharedExpenseForm(request.POST, user=user)
        if form.is_valid():
            participants_qs = form.cleaned_data['participants']
            split_type = form.cleaned_data['split_type']
            total_amount = form.cleaned_data['total_amount']

            # All participants = selected users + creator (payer)
            all_users = list(participants_qs) + [user]
            num_participants = len(all_users)

            # Validate manual split amounts
            if split_type == 'manual':
                manual_shares = {}
                total_manual = Decimal('0')
                errors = []
                for u in all_users:
                    key = f'share_{u.pk}'
                    val = request.POST.get(key, '').strip()
                    try:
                        amt = Decimal(val)
                        if amt < 0:
                            errors.append(f"Share for {u.email} cannot be negative.")
                        manual_shares[u.pk] = amt
                        total_manual += amt
                    except Exception:
                        errors.append(f"Invalid amount for {u.email}.")
                if errors:
                    for e in errors:
                        messages.error(request, e)
                    return render(request, 'shared_expenses/shared_form.html',
                                  {'form': form, 'all_users': all_users, 'currency': user.get_currency_symbol()})
                if abs(total_manual - total_amount) > Decimal('0.01'):
                    messages.error(request, f'Manual shares total ({total_manual}) must equal total amount ({total_amount}).')
                    return render(request, 'shared_expenses/shared_form.html',
                                  {'form': form, 'all_users': all_users, 'currency': user.get_currency_symbol()})

            with transaction.atomic():
                shared_expense = form.save(commit=False)
                shared_expense.created_by = user
                shared_expense.save()

                # Create participants
                equal_share = (total_amount / num_participants).quantize(Decimal('0.01'))
                for u in all_users:
                    if split_type == 'equal':
                        share = equal_share
                    else:
                        share = manual_shares[u.pk]
                    is_payer = (u == user)
                    Participant.objects.create(
                        shared_expense=shared_expense,
                        user=u,
                        share_amount=share,
                        is_payer=is_payer,
                        amount_paid=share if is_payer else Decimal('0'),
                        is_settled=is_payer,
                    )

            messages.success(request, f'Shared expense "{shared_expense.title}" created successfully!')
            return redirect('shared_expense_detail', pk=shared_expense.pk)
        else:
            # Show selected participants for manual form
            selected_ids = request.POST.getlist('participants')
            all_users = list(CustomUser.objects.filter(pk__in=selected_ids)) + [user]
    else:
        form = SharedExpenseForm(user=user)
        all_users = []

    return render(request, 'shared_expenses/shared_form.html', {
        'form': form, 'all_users': all_users, 'currency': user.get_currency_symbol()
    })


@login_required
def shared_expense_detail(request, pk):
    user = request.user
    se = get_object_or_404(SharedExpense, pk=pk)

    # Verify user is a participant
    my_participant = Participant.objects.filter(shared_expense=se, user=user).first()
    if not my_participant:
        messages.error(request, 'You are not a participant in this expense.')
        return redirect('shared_expense_list')

    participants = se.participants.select_related('user').all()
    settlements = Settlement.objects.filter(participant__shared_expense=se).order_by('-paid_at')

    context = {
        'se': se,
        'participants': participants,
        'settlements': settlements,
        'my_participant': my_participant,
        'currency': user.get_currency_symbol(),
        'is_fully_settled': se.is_fully_settled(),
    }
    return render(request, 'shared_expenses/shared_detail.html', context)


@login_required
def settle_payment(request, participant_pk):
    """Record a (partial) payment for a participant."""
    participant = get_object_or_404(Participant, pk=participant_pk, user=request.user)

    if participant.is_payer:
        messages.info(request, 'You are the payer — nothing to settle.')
        return redirect('shared_expense_detail', pk=participant.shared_expense.pk)

    if participant.is_settled:
        messages.info(request, 'This debt is already fully settled.')
        return redirect('shared_expense_detail', pk=participant.shared_expense.pk)

    if request.method == 'POST':
        form = SettlementForm(request.POST)
        via_upi = request.POST.get('via_upi') == '1'
        if form.is_valid():
            payment = form.cleaned_data['amount']
            max_due = participant.amount_due()

            if payment <= 0:
                messages.error(request, 'Payment must be greater than 0.')
            elif payment > max_due:
                messages.error(request, f'Overpayment! You only owe {request.user.get_currency_symbol()}{max_due}.')
            else:
                with transaction.atomic():
                    Settlement.objects.create(
                        participant=participant,
                        amount=payment,
                        note=form.cleaned_data.get('note', ''),
                        via_upi=via_upi,
                    )
                    participant.amount_paid += payment
                    participant.save()  # save() auto-settles when fully paid

                method = 'via UPI' if via_upi else ''
                messages.success(request, f'Payment of {request.user.get_currency_symbol()}{payment} recorded {method}.')
                return redirect('shared_expense_detail', pk=participant.shared_expense.pk)
    else:
        form = SettlementForm()

    context = {
        'form': form,
        'participant': participant,
        'amount_due': participant.amount_due(),
        'currency': request.user.get_currency_symbol(),
    }
    return render(request, 'shared_expenses/settle_form.html', context)
