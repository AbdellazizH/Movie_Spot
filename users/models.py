from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass


class UserList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="user")
    name = models.CharField(max_length=100, verbose_name="name")
    date = models.DateTimeField(auto_now_add=True, verbose_name="date")

    def __str__(self):
        return self.name


class ListItem(models.Model):
    list = models.ForeignKey(UserList, on_delete=models.CASCADE, verbose_name="list")
    movie_id = models.CharField(max_length=255, verbose_name="movie_id")
    movie_title = models.CharField(max_length=255, verbose_name="movie_title")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="date_added")

    def __str__(self):
        return f"Movie Id {self.movie_id} in {self.list}"
