from django.shortcuts import render


def index(request):
    return render(request, "main/main_page.html")

