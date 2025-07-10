from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=150, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)