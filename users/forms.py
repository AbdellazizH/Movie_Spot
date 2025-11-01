from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
