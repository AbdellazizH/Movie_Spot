from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import FormView
from users.forms import RegisterUserForm, CreateListForm
from users.models import UserList, ListItem


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


@login_required
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


@login_required
def delete_list(request, list_id):
    user_list = get_object_or_404(UserList, pk=list_id, user=request.user)
    if request.method == "POST":
        user_list.delete()
        user_lists = UserList.objects.filter(user=request.user)

        return render(request, "users/lists/partials/_user_lists.html", {"user_lists": user_lists})
    return HttpResponseForbidden


@login_required
def add_to_list(request, list_id, movie_id, movie_name):
    user_list = get_object_or_404(UserList, pk=list_id, user=request.user)

    if ListItem.objects.filter(movie_id=movie_id, list=user_list).exists():
        message = f"{movie_name} is already added to {user_list}"
        status = "danger"
    else:
        ListItem.objects.create(movie_id=movie_id, movie_name=movie_name, list=user_list)
        message = f"{movie_name} is added to {user_list}"
        status = "success"

    context = {"user_list": user_list, "message": message, "status": status}
    return render(request, "users/toasts/_confirmation_toast.html", context)

