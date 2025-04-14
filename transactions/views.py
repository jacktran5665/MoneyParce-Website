from django.shortcuts import render, redirect
from dashboard.models import Income, Expense, Budget
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def transaction_history(request):
    # Get filter parameters from the request
    transaction_type = request.GET.get('type', 'all')
    category_id = request.GET.get('category', None)

    # Base querysets - order by id since created_at isn't available
    incomes = Income.objects.all().order_by('-id')  # Latest first based on ID
    expenses = Expense.objects.all().order_by('-id')  # Latest first based on ID

    # Apply filters
    if transaction_type == 'income':
        expenses = Expense.objects.none()
    elif transaction_type == 'expense':
        incomes = Income.objects.none()

    if category_id and category_id.isdigit():
        expenses = expenses.filter(category_id=category_id)

    # Combine income and expenses into one list of transactions
    transactions = []

    for income in incomes:
        transactions.append({
            'type': 'Income',
            'amount': income.amount,
            'category': 'Income',
            'id': income.id
        })

    for expense in expenses:
        transactions.append({
            'type': 'Expense',
            'amount': expense.amount,
            'category': expense.category.name,
            'id': expense.id
        })

    # Sort transactions by id (newest first)
    transactions.sort(key=lambda x: x['id'], reverse=True)

    # Pagination (showing 20 transactions per page)
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)

    try:
        transactions_page = paginator.page(page)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    # Get all budget categories for filtering
    budgets = Budget.objects.all().order_by('name')

    context = {
        'transactions': transactions_page,
        'budgets': budgets,
        'selected_type': transaction_type,
        'selected_category': category_id,
    }

    return render(request, 'transactions/history.html', context)


def delete_transaction(request):
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        transaction_id = request.POST.get('transaction_id')

        if transaction_type == 'income':
            try:
                income = Income.objects.get(id=transaction_id)
                income.delete()
            except Income.DoesNotExist:
                pass
        elif transaction_type == 'expense':
            try:
                expense = Expense.objects.get(id=transaction_id)
                expense.delete()
            except Expense.DoesNotExist:
                pass

        # Redirect back to the page where the delete request came from
        next_url = request.POST.get('next', 'transactions_history')
        return redirect(next_url)

    # If not a POST request, redirect to transaction history
    return redirect('transactions_history')