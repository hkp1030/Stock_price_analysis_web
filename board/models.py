from django.db import models


class Board(models.Model):
    title = models.CharField(max_length=200, verbose_name="제목")
    contents = models.TextField(verbose_name="내용")
    writer = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name="작성자")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="최종수정일")
    hits = models.PositiveIntegerField(default=0, verbose_name="조회수")
    category = models.CharField(max_length=10, verbose_name="카테고리")
    locate = models.IntegerField(default=0, verbose_name="상단고정")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'boards'
        verbose_name = '게시판'
        verbose_name_plural = '게시판'
