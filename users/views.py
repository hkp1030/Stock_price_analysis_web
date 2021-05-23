from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import UserForm


# Create your views here.

def login_view(request):
    if request.method == "GET":
        return render(request, 'users/login.html')

    elif request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        res_data = {}
        if not (username and password):
            res_data['error'] = '모든 값을 입력하세요!'

        else:
            user = User.objects.get(username=username)
            # print(member.id)

            if check_password(password, user.password):
                # print(request.session.get('user'))
                request.session['user'] = user.id
                login(request, user)
                return redirect('/')


            else:
                res_data['error'] = '비밀번호가 다릅니다!'

        return render(request, 'users/login.html', res_data)


def logout_view(request):
    logout(request)
    return redirect("users:login")


def signup_view(request):
    # print(request.POST)
    if request.method == "POST":
        form = UserForm(request.POST)
        # print(form)

        if form.is_valid():
            print("성공")
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
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
