import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView

from django.http import HttpResponseForbidden, request
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from djangoProjectPikoCanFlyMovieSpot import settings
from .forms import RegisterUserForm, CreateListForm
from .models import UserList, ListItem


API_KEY = settings.TMDB_API_KEY


class Login(LoginView):
    template_name = "users/accounts/login.html"

    def get_success_url(self):
        return reverse_lazy("profile")


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
    return render(request, "users/lists/partials/_create_list_form.html", context)


@login_required
def delete_list(request, list_id):
    user_list = get_object_or_404(UserList, pk=list_id, user=request.user)
    if request.method == "POST":
        user_list.delete()
        user_lists = UserList.objects.filter(user=request.user)

        return render(request, "users/lists/partials/_user_lists.html", {"user_lists": user_lists})
    return HttpResponseForbidden


@login_required
def add_to_list(request, movie_id, movie_title, list_id):
    user_list = get_object_or_404(UserList, pk=list_id, user=request.user)

    if ListItem.objects.filter(list=user_list, movie_id=movie_id, movie_title=movie_title).exists():
        message = f"{movie_title} already in"
        color_message = "danger"
    else:
        ListItem.objects.create(list=user_list, movie_id=movie_id, movie_title=movie_title)
        message = f"{movie_title} added to {user_list}"
        color_message = "success"

    context = {"message": message, "color_message": color_message, "user_list": user_list}
    return render(request, "users/toasts/_confirmation_toasts.html", context)


def list_detail(request, list_id):
    user_list = get_object_or_404(UserList, id=list_id)
    list_items = ListItem.objects.filter(list=user_list)
    base_url = "https://api.themoviedb.org/3/movie/"

    movies = []
    for item in list_items:
        movie_id = item.movie_id
        url = f"{base_url}{movie_id}?api_key={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            movie = response.json()
            movies.append(movie)

    context = {
        "movies": movies,
        "user_list": user_list,
        "list_items": list_items,
        "is_owner": request.user.is_authenticated and request.user == user_list.user}
    return render(request, "users/lists/user_list_detail.html", context)


@login_required
def delete_movie(request, movie_id, list_id):
    user_list = get_object_or_404(UserList, pk=list_id, user=request.user)
    movie = get_object_or_404(ListItem, movie_id=movie_id, list=user_list)
    if request.method == "POST":
        movie.delete()
        list_items = ListItem.objects.filter(list=user_list)
        base_url = "https://api.themoviedb.org/3/movie/"

        movies = []
        for item in list_items:
            movie_id = item.movie_id
            url = f"{base_url}{movie_id}?api_key={API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                movie = response.json()
                movies.append(movie)
        context = {
            "movies": movies,
            "user_list": user_list,
            "list_items": list_items,
            "is_owner": request.user.is_authenticated and request.user == user_list.user}
        return render(request, "users/lists/partials/_updated_list.html", context)
    return HttpResponseForbidden
