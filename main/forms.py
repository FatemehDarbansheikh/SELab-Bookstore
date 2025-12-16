from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='ایمیل')
    phone = forms.CharField(label='شماره تماس', required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
