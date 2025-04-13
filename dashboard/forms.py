from django import forms
from .models import Income, Expense, Budget

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category']
