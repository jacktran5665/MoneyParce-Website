from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from .models import Income, Expense, Budget

@login_required
def transaction_history(request):
    ttype       = request.GET.get('type', 'all')
    category_id = request.GET.get('category')

    # Scope to this user and sort by newest first
    incomes  = Income.objects.filter(user=request.user).order_by('-created_at')
    expenses = Expense.objects.filter(user=request.user).order_by('-created_at')

    if ttype == 'income':
        expenses = Expense.objects.none()
    elif ttype == 'expense':
        incomes = Income.objects.none()

    if category_id and category_id.isdigit():
        expenses = expenses.filter(category_id=category_id)

    transactions = []
    for inc in incomes:
        transactions.append({
            'type':     'Income',
            'amount':   inc.amount,
            'category': 'Income',
            'date':     inc.created_at,
            'id':       inc.id,
        })
    for exp in expenses:
        transactions.append({
            'type':     'Expense',
            'amount':   exp.amount,
            'category': exp.category.name if exp.category else "Automatic",
            'date':     exp.created_at,
            'id':       exp.id,
        })

    # Sort the combined list by datetime (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)

    # Paginate
    page      = request.GET.get('page', 1)
    paginator = Paginator(transactions, 7)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    budgets = Budget.objects.filter(user=request.user).order_by('name')

    return render(request, 'transactions/history.html', {
        'transactions':      page_obj,
        'budgets':           budgets,
        'selected_type':     ttype,
        'selected_category': category_id,
    })


@login_required
def delete_transaction(request):
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        transaction_id = request.POST.get('transaction_id')

        if transaction_type == 'income':
            try:
                income = Income.objects.get(id=transaction_id, user=request.user)
                income.delete()
            except Income.DoesNotExist:
                pass
        elif transaction_type == 'expense':
            try:
                expense = Expense.objects.get(id=transaction_id, user=request.user)
                expense.delete()
            except Expense.DoesNotExist:
                pass

        # Redirect back to the page where the delete request came from
        next_url = request.POST.get('next', 'transactions_history')
        return redirect(next_url)

    # If not a POST request, redirect to transaction history
    return redirect('transactions_history')