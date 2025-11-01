from django.contrib.auth import login
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import FormView
from users.forms import RegisterUserForm


class Login(LoginView):
    template_name = "users/accounts/login.html"
    next_page = "/"


class Logout(LogoutView):
    next_page = "/"


class RegisterUser(FormView):
    template_name = "users/accounts/register.html"
    form_class = RegisterUserForm
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
