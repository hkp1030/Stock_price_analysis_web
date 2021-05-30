from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('list/', views.board_list, name='list'),
    path('write/', views.board_write, name='write'),
    path('detail/<int:pk>/', views.board_detail, name='detail'),
    path('<int:pk>/edit/', views.board_edit, name='edit'),
    path('<int:pk>/delete/', views.board_delete, name='delete'),
    path('search/', views.board_search, name='search'),
]
