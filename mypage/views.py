from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

# Create your views here.
import users
from users.models import User

@login_required(login_url='users:login')
def userInfo(request):
    info_user = request.user
    context = {
        'id': info_user,
        'name': info_user.name,
        'nick': info_user.n_name,
        'sex': info_user.sex,
        'birth': info_user.birth,
        'email': info_user.email,

    }
    return render(request, 'mypage/mypage.html', context=context)


def delete(request):
    if request.user.is_authenticated:
        request.user.delete()
        users.views.logout_view(request)  # 세션 지워주기

    return redirect('users:login')


def password(request):
    if request.method == 'POST':
        password_change_form = PasswordChangeForm(request.user, request.POST)

        # 키워드인자명을 함께 써줘도 가능
        # password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            users.views.logout_view(request)
            return redirect('users:login')

    else:
        password_change_form = PasswordChangeForm(request.user)
    return render(request, 'mypage/password.html', { 'password_change_form': password_change_form })