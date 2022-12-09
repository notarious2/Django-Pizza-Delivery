from django.shortcuts import render
from .forms import UserRegisterForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.contrib.auth import logout
from django.shortcuts import redirect


class SignUpView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    form_class = UserRegisterForm


class MyLoginView(LoginView):
    success_url = reverse_lazy('store:products')
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('store:products'))
        return super(LoginView, self).get(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return redirect('store:products')

# Create your views here.
