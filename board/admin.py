from django.contrib import admin
from board.models import Post
# Register your models here.

#admin.site.register(Post)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'mod_date')
    list_filter =  ('mod_date',)
    search_fields = ('title', 'content')

