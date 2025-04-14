from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Budget(models.Model):
    name = models.CharField(max_length=100)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def expenses_total(self):
        result = self.expense_set.aggregate(total=models.Sum('amount'))['total']
        return result if result is not None else 0

    def __str__(self):
        return f"{self.name} - ${self.total_budget}"

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Income: ${self.amount}"

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Budget, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Expense: ${self.amount} for {self.category.name}"