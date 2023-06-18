from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from base.models import Room, User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "email", "username", "name", "about"]
        exclude =[""]


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = [
            "topic",
            "room_name",
            "description",
        ]
        # exclude = ['host', 'participants']


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "name", "username", "password1", "password2"]
