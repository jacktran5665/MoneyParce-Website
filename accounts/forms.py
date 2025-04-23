from django import forms
from django.contrib.auth.forms import UserCreationForm
from home.models import Profile

class CustomUserCreationForm(UserCreationForm):
    budget = forms.IntegerField(
        required=True,
        label="What's your budget? (Security Question)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "What's your budget? (Security Question)"})
    )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
