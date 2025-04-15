from django.db import models
from django.db.models import Sum

class Budget(models.Model):
    name = models.CharField(max_length=100)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)

    def expenses_total(self):
        result = self.expense_set.aggregate(total=Sum('amount'))['total']
        return result if result is not None else 0

    def __str__(self):
        return f"{self.name} - ${self.total_budget}"

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Income: ${self.amount}"

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Instead of a text field, the expense is linked to a Budget object.
    category = models.ForeignKey(Budget, on_delete=models.CASCADE)

    def __str__(self):
        return f"Expense: ${self.amount} for {self.category.name}"

