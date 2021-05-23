from django.shortcuts import render

from users.models import User


def index(request):
    user_id = request.session.get('user')
    if user_id:
        user = User.objects.get(pk=user_id)
        return render(request, "main/main_page.html", {"user": user})
    return render(request, "main/main_page.html")
