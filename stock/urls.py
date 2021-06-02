from django.urls import path
from stock import views

app_name = 'stock'

urlpatterns = [
    path('<str:stock_id>', views.detail, name='detail'),
    path('index/', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('',views.move_board,name='board'),

]
