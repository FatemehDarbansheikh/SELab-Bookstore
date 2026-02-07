from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import Support, Address

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'phone': 'شماره تلفن',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'نام خانوادگی'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@email.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '09xxxxxxxxx'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('این نام کاربری قبلا استفاده شده است.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('این ایمیل قبلا ثبت شده است.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError('شماره تلفن باید فقط شامل عدد باشد.')
        return phone


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['country', 'city', 'street', 'postal_code', 'is_default']
        labels = {
            'country': 'کشور',
            'city': 'شهر',
            'street': 'آدرس',
            'postal_code': 'کد پستی',
            'is_default': 'آدرس پیش‌فرض',
        }
        widgets = {
            'country': forms.TextInput(attrs={'placeholder': 'کشور'}),
            'city': forms.TextInput(attrs={'placeholder': 'شهر'}),
            'street': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'خیابان، پلاک، واحد'
            }),
            'postal_code': forms.TextInput(attrs={'placeholder': 'کد پستی'}),
        }


class SupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['subject', 'message']
        labels = {
            'subject': 'موضوع',
            'message': 'پیام',
        }
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'موضوع پیام'}),
            'message': forms.Textarea(attrs={
                'placeholder': 'پیام خود را بنویسید...',
                'rows': 5
            }),
        }

    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message.strip()) < 10:
            raise ValidationError('متن پیام باید حداقل ۱۰ کاراکتر باشد.')
        return message
