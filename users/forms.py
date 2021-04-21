from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserForm(UserCreationForm):
    birth = forms.DateField(label="생년월일")
    email = forms.EmailField(label="이메일")
    name = forms.CharField(max_length=20, label="이름")
    sex = forms.CharField(max_length=10, label="성별")
    n_name = forms.CharField(max_length=20, label="닉네임")

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "name", "n_name","birth","sex", "email")