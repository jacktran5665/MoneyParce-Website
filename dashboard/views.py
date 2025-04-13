from django.shortcuts import render, redirect
from .models import Income, Expense, Budget
from decimal import Decimal

def dashboard_view(request):
    if request.method == 'POST':
        # Add Income
        if 'submit_income' in request.POST:
            income_amount = request.POST.get('income_amount')
            if income_amount:
                try:
                    amount = Decimal(income_amount)
                except Exception:
                    amount = Decimal("0.00")
                Income.objects.create(amount=amount)
                
        # Add Expense
        elif 'submit_expense' in request.POST:
            expense_amount = request.POST.get('expense_amount')
            expense_budget_id = request.POST.get('expense_budget')  # This should be a Budget id from the dropdown
            if expense_amount and expense_budget_id:
                try:
                    amount = Decimal(expense_amount)
                except Exception:
                    amount = Decimal("0.00")
                try:
                    budget_obj = Budget.objects.get(id=expense_budget_id)
                except Budget.DoesNotExist:
                    budget_obj = None
                if budget_obj:
                    Expense.objects.create(amount=amount, category=budget_obj)
                    
        # Add a new Budget (i.e. create a new category)
        elif 'submit_budget' in request.POST:
            budget_name = request.POST.get('budget_name')
            total_budget_input = request.POST.get('total_budget_new')
            if budget_name and total_budget_input:
                try:
                    amount = Decimal(total_budget_input)
                except Exception:
                    amount = Decimal("0.00")
                Budget.objects.create(name=budget_name, total_budget=amount)
                
    
    total_income = sum(item.amount for item in Income.objects.all())
    total_expenses = sum(item.amount for item in Expense.objects.all())
    remaining_balance = total_income - total_expenses

    budgets = Budget.objects.all().order_by('id')
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'budgets': budgets,
    }
    return render(request, 'dashboard/dashboard.html', context)
