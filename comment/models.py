from django.contrib.auth.models import User
from django.db import models

from board.models import Board


class Comment(models.Model):  # 세부내용은 필요에 따라..
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    content = models.CharField(max_length=300)
    writer = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name="작성자")
    create_date = models.DateTimeField()

    def __str__(self):
        return self.content
