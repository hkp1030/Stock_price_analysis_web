from django.shortcuts import render


# Create your views here.
def detail(request):
    return render(request, "stock/detail.html")
