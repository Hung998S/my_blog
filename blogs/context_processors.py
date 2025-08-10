# blogs/context_processors.py

from .models import Category, SubCategory

def categories_processor(request):
    categories = Category.objects.all()
    return {'categories': categories}

def subcategories_processor(request):
    subcategories = SubCategory.objects.select_related('category').all()
    return {'subcategories': subcategories}