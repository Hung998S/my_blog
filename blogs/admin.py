from django.contrib import admin
from .models import Category, SubCategory, Blog, DetailCountry


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'created_at', 'updated_at')


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'short_description', 'image', 'created_at', 'updated_at')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'detail_country', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'detail_country', 'author')
    search_fields = ('title', 'short_description', 'blog_body')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(DetailCountry)  # ✅ Đăng ký DetailCountry trong admin
