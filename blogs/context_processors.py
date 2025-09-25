# blogs/context_processors.py

from .models import Category, SubCategory, ChildCategory
from .views import get_youtube_channel


def categories_processor(request):
    categories = Category.objects.all()
    return {'categories': categories}

def subcategories_processor(request):
    subcategories = SubCategory.objects.select_related('category').all()
    return {'subcategories': subcategories}


def childcategories_processor(request):
    # Dùng prefetch_related để giảm số query
    childcategories = ChildCategory.objects.prefetch_related('detail_countries').all()
    return {'childcategories': childcategories}

def youtube_channel_context(request):
    return {
        "channel": get_youtube_channel()
    }