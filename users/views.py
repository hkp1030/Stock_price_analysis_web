from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import UserForm

import csv


# Create your views here.

def signup_view(request):
    # print(request.POST)

    if request.method == "POST":
        form = UserForm(request.POST)
        # print(form)

        if form.is_valid():
            form.save()
            return redirect('/auth/login')
    else:
        form = UserForm()
    return render(request, 'users/signup.html', {'form': form})


'''
    if request.method == "POST":
        print(request.POST)
        username = request.POST["username"]

        password = request.POST["password"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        email = request.POST["email"]

        user = User.objects.create_user(username, email, password)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        return redirect("users:login")

    return render(request, "users/signup.html")
'''
