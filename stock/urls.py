from django.urls import path
from stock import views

app_name = 'stock'

urlpatterns = [
    path('<str:stock_id>', views.detail, name='detail'),
    path('search/', views.search, name='search')

]
