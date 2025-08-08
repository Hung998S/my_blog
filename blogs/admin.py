from django.contrib import admin
from .models import Category, SubCategory, Blog


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'created_at', 'updated_at')


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'created_at', 'updated_at')


class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'status', 'is_featured', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'short_description', 'blog_body')
    list_filter = ('status', 'is_featured', 'created_at')
    ordering = ('-created_at',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Blog, BlogAdmin)
