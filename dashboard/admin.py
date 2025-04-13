from django.contrib import admin
from .models import Budget, Income, Expense

admin.site.register(Budget)
admin.site.register(Income)
admin.site.register(Expense)
