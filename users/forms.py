from django import forms
from .models import Customer, User
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
                user=user)
        return user


class CustomLoginForm(AuthenticationForm):
    """Modifying styling of login inputs"""
    username = forms.CharField(label='Email / Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'placeholder': 'Enter username or email',
             'class': 'w-64 px-3 py-2 rounded-md border border-slate-400'}
        )
        self.fields['password'].widget.attrs.update(
            {'placeholder': 'Enter password',
             'class': 'w-64 px-3 py-2 rounded-md border border-slate-400'}
        )


class CustomUserCreation(UserCreationForm):
    """Customizing User creation for use in admin panel"""
    class Meta:
        model = User
        fields = '__all__'
