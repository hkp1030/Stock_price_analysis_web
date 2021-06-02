from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, redirect
from django.db.models import Q
from django.views import generic

from users.models import User
from .forms import BoardForm
from .models import Board

from datetime import date, datetime, timedelta


def board_list(request):
    all_boards = Board.objects.all().order_by('-id')
    # 변수명을 all_boards 로 바꿔주었다.
    page = int(request.GET.get('p', 1))
    # p라는 값으로 받을거고, 없으면 첫번째 페이지로
    pagenator = Paginator(all_boards, 5)
    # Paginator 함수를 적용하는데, 첫번째 인자는 위에 변수인 전체 오브젝트, 2번째 인자는
    # 한 페이지당 오브젝트 10개씩 나오게 설정
    boards = pagenator.get_page(page)
    # 처음 2개가 세팅 된다.
    return render(request, 'board/board_list.html', {"boards": boards})


def board_write(request):
    if not request.session.get('user'):
        return redirect('/auth/login')
    # 세션에 'user' 키를 불러올 수 없으면, 로그인하지 않은 사용자이므로 로그인 페이지로 리다이렉트 한다.

    if request.method == "POST":
        form = BoardForm(request.POST)

        if form.is_valid():
            # form의 모든 validators 호출 유효성 검증 수행
            user_id = request.session.get('user')
            member = User.objects.get(pk=user_id)

            board = Board()
            board.title = form.cleaned_data['title']
            board.category = form.cleaned_data['category']
            board.contents = form.cleaned_data['contents']
            # 검증에 성공한 값들은 사전타입으로 제공 (form.cleaned_data)
            # 검증에 실패시 form.error 에 오류 정보를 저장

            board.writer = member
            board.save()

            return redirect('board:list')

    else:
        form = BoardForm()

    return render(request, 'board/board_write.html', {'form': form})


def board_detail(request, pk):
    try:
        board = Board.objects.get(pk=pk)
        board.hits += 1
        board.save()
    except Board.DoesNotExist:
        raise Http404('게시글을 찾을 수 없습니다')
        # 게시물의 내용을 찾을 수 없을 때 내는 오류 message.

    return render(request, 'board/board_detail.html', {'board': board})


def board_edit(request, pk):
    board = Board.objects.get(id=pk)

    if request.method == "POST":
        if board.writer == request.user:
            form = BoardForm(request.POST, instance=board)
            if form.is_valid():
                board = form.save(commit=False)
                board.save()
                messages.success(request, "수정되었습니다.")
                return redirect('/board/list')
    else:
        board = Board.objects.get(id=pk)
        if board.writer == request.user:
            form = BoardForm(instance=board)
            context = {
                'form': form,
                'edit': '수정하기',
            }
            return render(request, "board/board_write.html", context)
        else:

            return redirect('/board/list')


def board_delete(request, pk):
    board = Board.objects.get(id=pk)
    if board.writer == request.user:
        board.delete()
        return redirect('/board/list/')
    else:
        return redirect('/board/list/')


def board_search(request):
    board = Board.objects.all().order_by('-id')  # 모든 Border 테이블의 모든 object들을 br에 저장하라

    b = request.GET.get('b','')  # GET request의 인자중에 b 값이 있으면 가져오고, 없으면 빈 문자열 넣기
    f = request.GET.get('f','')

    if f == 't':
        if b:  # b에 값이 들어있으면 true
        # 의 title이 contains br의 title에 포함되어 있으면 br에 저장
            board = board.filter(title__icontains=b)
    elif f == 'c':
        if b:
            board = board.filter(contents__icontains=b)
    elif f == 'g':
        if b:
            board = board.filter(category__icontains=b)
    elif f == 'w':
        if b:
            board = board.filter(writer__n_name__icontains=b)

    page = int(request.GET.get('p', 1))

    # p라는 값으로 받을거고, 없으면 첫번째 페이지로

    pagenator = Paginator(board, 5)
    # Paginator 함수를 적용하는데, 첫번째 인자는 위에 변수인 전체 오브젝트, 2번째 인자는
    # 한 페이지당 오브젝트 10개씩 나오게 설정
    search_boards = pagenator.get_page(page)
    # 처음 2개가 세팅 된다.

    return render(request, 'board/board_search.html', {'board_search': search_boards, 'b': b})
