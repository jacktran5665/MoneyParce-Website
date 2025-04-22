from django.contrib.auth.decorators import login_required
from django.shortcuts              import render, redirect
from decimal                       import Decimal
from .models                       import Income, Expense, Budget

@login_required
def dashboard_view(request):
    if request.method == 'POST':
        if 'submit_income' in request.POST:
            amt = Decimal(request.POST.get('income_amount', '0') or '0')
            Income.objects.create(user=request.user, amount=amt)

        elif 'submit_expense' in request.POST:
            amt = Decimal(request.POST.get('expense_amount', '0') or '0')
            bid = request.POST.get('expense_budget')
            try:
                budget_obj = Budget.objects.get(id=bid, user=request.user)
            except Budget.DoesNotExist:
                budget_obj = None
            if budget_obj:
                Expense.objects.create(user=request.user,
                                       amount=amt,
                                       category=budget_obj)

        elif 'submit_budget' in request.POST:
            name = request.POST.get('budget_name','').strip()
            tot  = Decimal(request.POST.get('total_budget_new','0') or '0')
            if name:
                Budget.objects.create(user=request.user,
                                      name=name,
                                      total_budget=tot)

        return redirect('dashboard')

    # GET
    incomes  = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    budgets  = Budget.objects.filter(user=request.user).order_by('id')

    total_income      = sum(i.amount for i in incomes)
    total_expenses    = sum(e.amount for e in expenses)
    remaining_balance = total_income - total_expenses

    return render(request, 'dashboard/dashboard.html', {
        'total_income':      total_income,
        'total_expenses':    total_expenses,
        'remaining_balance': remaining_balance,
        'budgets':           budgets,
    })
