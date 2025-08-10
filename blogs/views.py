from django.shortcuts import render, get_object_or_404
from .models import Category, SubCategory, Blog


def home(request):
    categories = Category.objects.all()           
    subcategories = SubCategory.objects.all()     
    featured_post = Blog.objects.filter(is_featured = True ,status = 'published' )
    posts = Blog.objects.filter(is_featured = False, status='published')

    context = {
        'categories': categories,
        'subcategories': subcategories,      
        'featured_post': featured_post,
        'posts': posts     
    }

    return render(request, 'home.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = category.subcategories.all()
    return render(request, 'category_detail.html', {
        'category': category,
        'subcategories': subcategories
    })


def subcategory_detail(request, category_id):
    # Lấy category cha
    category = get_object_or_404(Category, id=category_id)
    # Lấy tất cả subcategory của category này
    subcategories = category.subcategories.all()
    # Lấy tất cả blog thuộc các subcategory này
    blogs = Blog.objects.filter(
        subcategory__in=subcategories,
        status='published'
    )
    # Bài nổi bật
    featured_post = Blog.objects.filter(is_featured=True, status='published')
    return render(request, 'subcategory_detail.html', {
        'category': category,
        'subcategories': subcategories,
        'blogs': blogs,
        'featured_post': featured_post,
    })

