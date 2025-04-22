from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone

class Budget(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     on_delete=models.CASCADE,
                                     null = True,
                                     related_name='budgets')
    name         = models.CharField(max_length=100)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)

    def expenses_total(self):
        return self.expenses.aggregate(total=Sum('amount'))['total'] or 0

    def __str__(self):
        return f"{self.name} — ${self.total_budget}"

class Income(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   null = True,
                                   related_name='incomes')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)      # ← new!

    def __str__(self):
        return f"Income: ${self.amount}"

class Expense(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   null = True,
                                   related_name='expenses')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    category   = models.ForeignKey(Budget,
                                   on_delete=models.CASCADE,
                                   null = True,
                                   related_name='expenses')
    created_at = models.DateTimeField(default=timezone.now)      # ← new!

    def __str__(self):
        return f"Expense: ${self.amount} — {self.category.name}"

class PlaidItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=120)
    item_id = models.CharField(max_length=100)
    institution_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} — {self.institution_name or 'Plaid Item'}"