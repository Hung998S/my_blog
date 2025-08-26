from django.shortcuts import render, redirect
from blogs.models import Category,SubCategory ,Blog
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
from django.conf import settings
from django.core.files.storage import default_storage

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
    if request.method == "POST":
        action = request.POST.get("action")
        cat_id = request.POST.get("cat_id")
        name = request.POST.get("name")

        if action == "add" and name:
            Category.objects.create(category_name=name)

        elif action == "edit" and cat_id and name:
            category = get_object_or_404(Category, id=cat_id)
            category.category_name = name
            category.save()

        elif action == "delete" and cat_id:
            category = get_object_or_404(Category, id=cat_id)
            category.delete()

        return redirect("categories")

    categories = Category.objects.all().order_by("-created_at")
    return render(request, "dashboard/categories.html", {"categories": categories})


def subcategories(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Thêm SubCategory
        if action == "add_sub":
            category_id = request.POST.get("category")
            name = request.POST.get("name")
            desc = request.POST.get("short_description")
            image = request.FILES.get("image")

            category = get_object_or_404(Category, id=category_id)
            sub = SubCategory.objects.create(
                category=category,
                name=name,
                short_description=desc,
                image=image,
            )
            messages.success(request, f"SubCategory '{name}' created successfully!")

        # Sửa SubCategory
        elif action == "edit_sub":
            sub_id = request.POST.get("sub_id")
            sub = get_object_or_404(SubCategory, id=sub_id)

            sub.category_id = request.POST.get("category")
            sub.name = request.POST.get("name")
            sub.short_description = request.POST.get("short_description")

            if request.FILES.get("image"):
                sub.image = request.FILES.get("image")

            sub.save()
            messages.success(request, f"SubCategory '{sub.name}' updated successfully!")

        # Xóa SubCategory
        elif action == "delete_sub":
            sub_id = request.POST.get("sub_id")
            sub = get_object_or_404(SubCategory, id=sub_id)
            sub.delete()
            messages.success(request, f"SubCategory '{sub.name}' deleted successfully!")

        return redirect("subcategories")  # trỏ về url name="subcategories"

    # GET request: load dữ liệu
    subs = SubCategory.objects.all()
    cats = Category.objects.all()
    return render(
        request,
        "dashboard/subcategories.html",
        {"subcategories": subs, "categories": cats},
    )


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


def add_blogs(request):
    if request.method == "POST":
        title = request.POST.get("title")
        sub_id = request.POST.get("subcategory")
        short_desc = request.POST.get("short_description")
        blog_body = request.POST.get("blog_body")
        status = request.POST.get("status", "draft")
        is_featured = request.POST.get("is_featured") == "on"
        image = request.FILES.get("blog_image")

        if title and sub_id and blog_body:
            sub = get_object_or_404(SubCategory, id=sub_id)
            Blog.objects.create(
                title=title,
                slug=title.lower().replace(" ", "-"),  # tự tạo slug
                subcategory=sub,
                author=request.user,
                short_description=short_desc,
                blog_body=blog_body,
                blog_image=image,
                is_featured=is_featured,
                status=status,
            )
            messages.success(request, f"Blog '{title}' created successfully!")
            return redirect("blogs")
        else:
            messages.error(request, "Title, SubCategory và Blog Body là bắt buộc!")

    subs = SubCategory.objects.all()
    return render(request, "dashboard/add_blogs.html", {"subcategories": subs})



@csrf_exempt
def upload_image(request):
    if request.method == "POST" and request.FILES.get("upload"):
        upload = request.FILES["upload"]
        saved_path = default_storage.save(upload.name, upload)
        url = default_storage.url(saved_path)
        # CKEditor 5 cần cả "uploaded":1 và "url"
        return JsonResponse({
            "uploaded": 1,
            "url": url
        })
    return JsonResponse({
        "uploaded": 0,
        "error": {"message": "Invalid request"}
    })
