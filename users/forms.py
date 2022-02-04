from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'style': 'direction: rtl; text-align: right;'}))
    #phone = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'style': 'direction: rtl;'}))    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']
