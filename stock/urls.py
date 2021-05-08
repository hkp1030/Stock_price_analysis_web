from django.urls import path
from stock import views

app_name = 'stock'

urlpatterns = [
    path('detail', views.detail, name='detail'),

]
