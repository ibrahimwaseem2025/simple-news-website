from django.contrib import admin
from .models import Category,News,Comment
from django.contrib import admin
from embed_video.admin import AdminVideoMixin




# Register your models here.
admin.site.register(Category,)

class AdminNews(admin.ModelAdmin,AdminVideoMixin):
    list_display=('title','category','add_time', 'location','author','number_of_likes', 'video','voice', 'podcast','opinion','featured','top_news','views')
    pass
admin.site.register(News,AdminNews)

class AdminComment(admin.ModelAdmin):
    list_display=('news','email','comment','status')
admin.site.register(Comment,AdminComment) 
# Register your models here.

