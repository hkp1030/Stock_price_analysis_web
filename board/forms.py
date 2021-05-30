from django.contrib.auth.hashers import check_password

from django import forms
from .models import Board

from django_summernote.widgets import SummernoteWidget


class BoardForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BoardForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = '제목'

        self.fields['title'].widget.attrs.update({
            'placeholder': '제목을 입력해주세요.',
            'class': 'form-control',
            'autofocus': True,
        })

        self.fields['category'].label = '카테고리'

    class Meta:
        model = Board
        fields = ['title', 'category', 'contents']
        widgets = {'contents': SummernoteWidget(), }
