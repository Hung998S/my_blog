from django.contrib import admin
from .models import Category, SubCategory, Blog


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'created_at', 'updated_at')


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'short_description', 'image', 'created_at', 'updated_at')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'category','author','blog_image','status', 'is_featured','created_at','updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('id', 'title', 'category__name', 'status')
    list_editable = ( 'is_featured',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
