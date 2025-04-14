import json
from django.shortcuts import render
from dashboard.models import Budget

def budget_chart(request):
    chart_data = [['Category', 'Used', 'Remaining']]  # Header row for Google Charts

    for budget in Budget.objects.all():
        used = float(budget.expenses_total())
        total = float(budget.total_budget)
        remaining = max(total - used, 0)
        chart_data.append([budget.name, used, remaining])

    context = {
        'chart_data_json': json.dumps(chart_data),  # Convert safely to JSON
    }
    return render(request, 'reports/budget_summary.html', context)

