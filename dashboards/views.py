from django.shortcuts import render
from blogs.models import Category,SubCategory ,Blog
from django.shortcuts import render, get_object_or_404


# Create your views here.
def dashboard(request):
    category_counts = Category.objects.all().count()
    subcategories_counts = SubCategory.objects.all().count()
    blogs_counts = Blog.objects.all().count()

    context = {
        'category_counts' : category_counts,
        'subcategories_counts' : subcategories_counts,
        'blogs_counts': blogs_counts
    }

    return render(request, 'dashboard/dashboard.html', context)


def categories(request):
    return render(request, 'dashboard/categories.html')


def subcategories(request):
    subs = SubCategory.objects.all()
    return render(request, 'dashboard/subcategories.html', {"subcategories": subs})


def blogs(request):
    sub_id = request.GET.get('id')  # lấy id subcategory từ query string
    if sub_id:
        posts = Blog.objects.filter(subcategory_id=sub_id).order_by('-created_at')
    else:
        posts = Blog.objects.all().order_by('-created_at')

    context = {
        'posts': posts,
    }
    return render(request, 'dashboard/blogs.html', context)

def subcategory_detail(request, sub_id):
    sub = get_object_or_404(SubCategory, id=sub_id)
    blogs = Blog.objects.filter(subcategory=sub).order_by('-created_at')
    context = {
        'sub': sub,
        'posts': blogs
    }
    return render(request, 'dashboard/blogs.html', context)