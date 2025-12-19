from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import Support

User = get_user_model()


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'password': 'رمز عبور',
            'phone': 'شماره تلفن',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09xxxxxxxxx'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError('شماره تلفن باید فقط شامل عدد باشد.')
        return phone
    


class SupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['subject', 'message']
        labels = {
            'subject': 'موضوع',
            'message': 'پیام',
        }
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع پیام'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'پیام خود را بنویسید...',
                'rows': 5
            }),
        }

    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message.strip()) < 10:
            raise ValidationError('متن پیام باید حداقل ۱۰ کاراکتر باشد.')
        return message
