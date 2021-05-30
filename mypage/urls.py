from django.urls import path

from . import views

app_name = 'mypage'

urlpatterns = [
    path('info/', views.userInfo, name='mypage'),
    path('delete/', views.delete, name='delete'),
    path('password/', views.password, name='password'),
]
