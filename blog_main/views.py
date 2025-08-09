from django.shortcuts import render
from blogs.models import Category, SubCategory, Blog

def home(request):
    categories = Category.objects.all()           
    subcategories = SubCategory.objects.all()     
    featured_post = Blog.objects.filter(is_featured = True )

    context = {
        'categories': categories,
        'subcategories': subcategories,      
        'featured_post': featured_post     
    }

    return render(request, 'home.html', context)
