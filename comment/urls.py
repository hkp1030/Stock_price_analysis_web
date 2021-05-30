from django.urls import path

from . import views

app_name = 'comment'

urlpatterns = [
    path('answer/create/<int:board_id>/', views.answer_create, name='answer_create'),
    path('answer/delete/<int:comment_id>/', views.answer_delete, name='answer_delete'),

]