from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from board.models import Board
from comment.models import Comment
from users.models import User


@login_required(login_url='users:login')
def answer_create(request, board_id):

    board = get_object_or_404(Board, pk=board_id)
    member = request.user
    comment = Comment(board=board, content=request.POST.get('content'), create_date=timezone.now(), writer=member)
    comment.save()
    return redirect('board:detail', pk=board.id)


def answer_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    member = request.user
    if member == comment.writer:
        print("2")
        comment.delete()
    elif member == comment.board.writer:
        print("3")
        comment.delete()
    elif member.n_name == '관리자':
        print("4")
        comment.delete()
    else:
        print("1")
        messages.error(request, '삭제권한이 없습니다')

    return redirect('board:detail', pk=comment.board.id)
