from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    birth = models.DateField(default="2000-01-01",verbose_name="생년월일")
    email = models.EmailField(unique=True, verbose_name="이메일")
    name = models.CharField(max_length=20, verbose_name="이름")
    sex = models.CharField(max_length=10, verbose_name="성별")
    n_name = models.CharField(max_length=20, unique=True, verbose_name="닉네임")
