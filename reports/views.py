import json, datetime
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from dashboard.models import Budget, Expense 

@login_required
def budget_chart(request):
    chart_data = [['Category', 'Used', 'Remaining']]  
    for budget in Budget.objects.filter(user=request.user):
        used       = float(budget.expenses_total())
        total      = float(budget.total_budget)
        remaining  = max(total - used, 0)
        chart_data.append([budget.name, used, remaining])

    context = {
        'chart_data_json': json.dumps(chart_data)  
    }
    return render(request, 'reports/budget_summary.html', context)
def budget_chart(request):
    category_data = [['Category', 'Used', 'Remaining']]
    for b in Budget.objects.filter(user=request.user):
        used = float(b.expenses_total())
        total = float(b.total_budget)
        category_data.append([b.name, used, max(total - used, 0)])
    today       = timezone.localdate()
    month_start = today.replace(day=1)

    daily_qs = (
        Expense.objects.filter(user=request.user,
                               created_at__date__gte=month_start,   # adjust if your field is named differently
                               created_at__date__lte=today)
               .annotate(day=TruncDate('created_at'))
               .values('day')
               .order_by('day')
               .annotate(total=Sum('amount'))
    )
    daily_data = [['Date', 'Spent']]
    for row in daily_qs:
        d = row['day']
        daily_data.append([f"{d.month}/{d.day}/{d.year}", float(row['total'])])

    context = {
        'category_json': json.dumps(category_data),
        'daily_json':    json.dumps(daily_data),
    }
    return render(request, 'reports/budget_summary.html', context)