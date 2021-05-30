from django.contrib import admin

from .models import Board


class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'created_at', 'updated_at')

admin.site.register(Board, BoardAdmin)
