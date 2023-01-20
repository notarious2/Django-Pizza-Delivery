from django import forms
from django.contrib.auth.models import User
from .models import Customer
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'w-64 px-3 py-2 rounded-md border border-slate-400', 'placeholder': 'Your Email'}))
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'w-64 px-3 py-2 rounded-md border border-slate-400', 'placeholder': 'Your Username',
               }))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'w-64 px-3 py-2 rounded-md border border-slate-400', 'placeholder': 'Your Password',
               }))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'w-64 px-3 py-2 rounded-md border border-slate-400', 'placeholder': 'Re-type Password',
               }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        if commit:
            user.save()
            Customer.objects.create(
                user=user, username=user.username)
        return user


class CustomLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'placeholder': 'Your Username',
             'class': 'w-64 px-3 py-2 rounded-md border border-slate-400'}
        )
        self.fields['password'].widget.attrs.update(
            {'placeholder': 'Your Password',
             'class': 'w-64 px-3 py-2 rounded-md border border-slate-400'}
        )
