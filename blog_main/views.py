from django.shortcuts import render
from blogs.models import Category, SubCategory

def home(request):
    categories = Category.objects.all()           
    subcategories = SubCategory.objects.all()     

    context = {
        'categories': categories,
        'subcategories': subcategories,           
    }

    return render(request, 'home.html', context)
