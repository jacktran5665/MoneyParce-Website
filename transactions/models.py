from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from decimal import Decimal
from dashboard.models import Income, Expense, Budget

@login_required
def transaction_history(request):
    ttype       = request.GET.get('type', 'all')
    category_id = request.GET.get('category')

    # 1) Scope & order by real timestamp
    incomes  = Income.objects.filter(user=request.user).order_by('-created_at')
    expenses = Expense.objects.filter(user=request.user).order_by('-created_at')

    # 2) Apply type filter
    if ttype == 'income':
        expenses = Expense.objects.none()
    elif ttype == 'expense':
        incomes = Income.objects.none()

    # 3) Apply category filter (only expenses have a category)
    if category_id and category_id.isdigit():
        expenses = expenses.filter(category_id=category_id)

    # 4) Build a unified list, carrying date & description
    transactions = []
    for inc in incomes:
        transactions.append({
            'type':        'Income',
            'id':          inc.id,
            'amount':      inc.amount,
            'category':    'Income',
            'date':        inc.created_at,
            'description': inc.description or '',
        })
    for exp in expenses:
        transactions.append({
            'type':        'Expense',
            'id':          exp.id,
            'amount':      exp.amount,
            'category':    exp.category.name,
            'date':        exp.created_at,
            'description': exp.description or '',
        })

    # 5) Sort by date (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)

    # 6) Paginate (10 per page)
    page      = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # 7) Budgets dropdown (also scoped to user)
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
        ttype = request.POST.get('transaction_type')
        tid   = request.POST.get('transaction_id')

        if ttype == 'income':
            Income.objects.filter(id=tid, user=request.user).delete()
        elif ttype == 'expense':
            Expense.objects.filter(id=tid, user=request.user).delete()

        return redirect(request.POST.get('next', 'transactions_history'))

    return redirect('transactions_history')
