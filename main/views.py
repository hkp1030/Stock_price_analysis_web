from django.shortcuts import render

from users.models import User


def index(request):
    return render(request, "main/main_page.html")
