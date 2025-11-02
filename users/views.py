from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import FormView
from users.forms import RegisterUserForm, CreateListForm
from users.models import UserList


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


@login_required
def profile(request):
    user = request.user
    user_lists = UserList.objects.filter(user=user)

    context = {"user": user, "user_lists": user_lists}
    return render(request, "users/accounts/profile.html", context)


def create_list(request):
    user = request.user
    if request.method == "POST":
        form = CreateListForm(request.POST)
        if form.is_valid():
            user_list = form.save(commit=False)
            user_list.user = user
            user_list.save()
            user_lists = UserList.objects.filter(user=user)
            return render(request, "users/lists/partials/_user_lists.html", {"user_lists": user_lists})
        return render(request, "users/lists/partials/_user_lists.html", {"form": form}, status=400)

    form = CreateListForm()
    context = {"form": form}
    return render(request, 'users/lists/partials/_create_list_form.html', context)
