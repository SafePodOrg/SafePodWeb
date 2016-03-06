from django.contrib import admin

from .models import Post, Tag, Comment, AppUser

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {}   

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    
class CommentAdmin(admin.ModelAdmin):
    prepopulated_fields = {}   

class AppUserAdmin(admin.ModelAdmin):
    prepopulated_fields = {}

admin.site.register(Post,PostAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(AppUser,AppUserAdmin)
