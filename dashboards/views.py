from django.shortcuts import render, redirect
from blogs.models import Category,SubCategory ,Blog, ChildCategory, Country  ,DetailCountry
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator


# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
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
        icon = request.FILES.get("icon")  # Lấy file icon từ form

        # ADD
        if action == "add" and name:
            Category.objects.create(category_name=name, icon=icon)

        # EDIT
        elif action == "edit" and cat_id and name:
            category = get_object_or_404(Category, id=cat_id)
            category.category_name = name
            # Nếu có file icon mới thì cập nhật icon
            if icon:
                category.icon = icon
            category.save()

        # DELETE
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
            icon = request.FILES.get("icon")  # ✅ Lấy file icon từ form

            category = get_object_or_404(Category, id=category_id)
            sub = SubCategory.objects.create(
                category=category,
                name=name,
                short_description=desc,
                image=image,
                icon=icon,  # ✅ Lưu icon
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

            if request.FILES.get("icon"):  # ✅ Nếu có icon mới thì cập nhật
                sub.icon = request.FILES.get("icon")

            sub.save()
            messages.success(request, f"SubCategory '{sub.name}' updated successfully!")

        # Xóa SubCategory
        elif action == "delete_sub":
            sub_id = request.POST.get("sub_id")
            sub = get_object_or_404(SubCategory, id=sub_id)
            sub.delete()
            messages.success(request, f"SubCategory '{sub.name}' deleted successfully!")

        return redirect("subcategories")

    # GET request: load dữ liệu
    subs = SubCategory.objects.all()
    cats = Category.objects.all()
    return render(
        request,
        "dashboard/subcategories.html",
        {"subcategories": subs, "categories": cats},
    )


def childcategories(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Thêm ChildCategory
        if action == "add_child":
            subcategory_id = request.POST.get("subcategory")
            title = request.POST.get("title")
            desc = request.POST.get("short_description")
            image = request.FILES.get("image")

            subcategory = get_object_or_404(SubCategory, id=subcategory_id)
            ChildCategory.objects.create(
                subcategory=subcategory,
                title=title,
                short_description=desc,
                image=image,
            )
            messages.success(request, f"ChildCategory '{title}' created successfully!")

        # Sửa ChildCategory
        elif action == "edit_child":
            child_id = request.POST.get("child_id")
            child = get_object_or_404(ChildCategory, id=child_id)

            child.subcategory_id = request.POST.get("subcategory")
            child.title = request.POST.get("title")
            child.short_description = request.POST.get("short_description")

            if request.FILES.get("image"):
                child.image = request.FILES.get("image")

            child.save()
            messages.success(request, f"ChildCategory '{child.title}' updated successfully!")

        # Xóa ChildCategory
        elif action == "delete_child":
            child_id = request.POST.get("child_id")
            child = get_object_or_404(ChildCategory, id=child_id)
            child.delete()
            messages.success(request, f"ChildCategory '{child.title}' deleted successfully!")

        return redirect("childcategories")

    # GET request: load dữ liệu + phân trang
    children = ChildCategory.objects.all().order_by("-created_at")
    subcategories = SubCategory.objects.all()

    paginator = Paginator(children, 20)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/childcategories.html",
        {
            "childcategories": page_obj,
            "page_obj": page_obj,
            "subcategories": subcategories,
        },
    )
    
    
def countries(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # ➕ Thêm Country
        if action == "add_country":
            childcategory_id = request.POST.get("childcategory")
            name = request.POST.get("name")
            capital = request.POST.get("capital")
            geography = request.POST.get("geography")
            area = request.POST.get("area")
            population = request.POST.get("population")
            language = request.POST.get("language")
            government = request.POST.get("government")
            economy = request.POST.get("economy")
            currency = request.POST.get("currency")
            climate = request.POST.get("climate")
            flag = request.FILES.get("flag")
            map_image = request.FILES.get("map")

            childcategory = get_object_or_404(ChildCategory, id=childcategory_id)
            Country.objects.create(
                childcategory=childcategory,
                name=name,
                capital=capital,
                geography=geography,
                area=area,
                population=population,
                language=language,
                government=government,
                economy=economy,
                currency=currency,
                climate=climate,
                flag=flag,
                map=map_image
            )
            messages.success(request, f"Country '{name}' created successfully!")

        # ✏️ Sửa Country
        elif action == "edit_country":
            country_id = request.POST.get("country_id")
            country = get_object_or_404(Country, id=country_id)

            country.childcategory_id = request.POST.get("childcategory")
            country.name = request.POST.get("name")
            country.capital = request.POST.get("capital")
            country.geography = request.POST.get("geography")
            country.area = request.POST.get("area")
            country.population = request.POST.get("population")
            country.language = request.POST.get("language")
            country.government = request.POST.get("government")
            country.economy = request.POST.get("economy")
            country.currency = request.POST.get("currency")
            country.climate = request.POST.get("climate")

            if request.FILES.get("flag"):
                country.flag = request.FILES.get("flag")
            if request.FILES.get("map"):
                country.map = request.FILES.get("map")

            country.save()
            messages.success(request, f"Country '{country.name}' updated successfully!")

        # 🗑️ Xóa Country
        elif action == "delete_country":
            country_id = request.POST.get("country_id")
            country = get_object_or_404(Country, id=country_id)
            country.delete()
            messages.success(request, f"Country '{country.name}' deleted successfully!")

        return redirect("countries")

    # GET request: load danh sách + phân trang
    countries = Country.objects.all().order_by("name")
    childcategories = ChildCategory.objects.all()

    paginator = Paginator(countries, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/countries.html",
        {
            "countries": page_obj,
            "page_obj": page_obj,
            "childcategories": childcategories,
        },
    )
    
def detail_countries(request):
    detailcountries = DetailCountry.objects.all()
    childcategories = ChildCategory.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Thêm mới
        if action == 'add_detailcountry':
            child_id = request.POST.get('childcategory')
            name = request.POST.get('name')
            child = get_object_or_404(ChildCategory, id=child_id)
            DetailCountry.objects.create(childcategory=child, name=name)
            return redirect('detail_countries')

        # Chỉnh sửa
        elif action == 'edit_detailcountry':
            detail_id = request.POST.get('detailcountry_id')
            name = request.POST.get('name')
            child_id = request.POST.get('childcategory')
            detail = get_object_or_404(DetailCountry, id=detail_id)
            child = get_object_or_404(ChildCategory, id=child_id)
            detail.childcategory = child
            detail.name = name
            detail.save()
            return redirect('detail_countries')

        # Xóa
        elif action == 'delete_detailcountry':
            detail_id = request.POST.get('detailcountry_id')
            detail = get_object_or_404(DetailCountry, id=detail_id)
            detail.delete()
            return redirect('detail_countries')

    context = {
        'detailcountries': detailcountries,
        'childcategories': childcategories,
    }
    return render(request, 'dashboard/detail_countries.html', context)


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

def edit_blogs(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        title = request.POST.get("title")
        sub_id = request.POST.get("subcategory")
        short_desc = request.POST.get("short_description")
        blog_body = request.POST.get("blog_body")
        status = request.POST.get("status", "draft")
        is_featured = request.POST.get("is_featured") == "on"
        image = request.FILES.get("blog_image")

        # Debug thử
        print("=== DEBUG EDIT BLOG ===")
        print("FILES:", request.FILES)         # Xem có file nào không
        print("Image:", image)                 # Xem ảnh nhận vào là gì
        print("Old Image:", blog.blog_image)   # Xem ảnh cũ trong DB

        if title and sub_id and blog_body:
            sub = get_object_or_404(SubCategory, id=sub_id)

            blog.title = title
            blog.slug = title.lower().replace(" ", "-")
            blog.subcategory = sub
            blog.short_description = short_desc
            blog.blog_body = blog_body
            blog.is_featured = is_featured
            blog.status = status

            if image:  # nếu upload ảnh mới thì thay ảnh cũ
                print(">>> Updating image to:", image.name)
                blog.blog_image = image
            else:
                print(">>> Không có ảnh mới, giữ ảnh cũ.")

            blog.save()
            messages.success(request, f"Blog '{title}' updated successfully!")
            return redirect("blogs")
        else:
            messages.error(request, "Title, SubCategory và Blog Body là bắt buộc!")

    subs = SubCategory.objects.all()
    return render(request, "dashboard/edit_blogs.html", {
        "subcategories": subs,
        "blog": blog
    })


def delete_blogs(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # Nếu blog có ảnh → xóa file ảnh
    if blog.blog_image and os.path.isfile(blog.blog_image.path):
        os.remove(blog.blog_image.path)

    blog.delete()
    messages.success(request, f"Blog '{blog.title}' deleted successfully!")
    return redirect("blogs")



def users(request):
    if request.method == "POST":
        # Nếu là update (edit)
        if "edit_user_id" in request.POST:
            user_id = request.POST.get("edit_user_id")
            user = get_object_or_404(User, id=user_id)

            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.username = request.POST.get("username")
            user.email = request.POST.get("email")
            user.is_active = request.POST.get("is_active") == "true"
            user.is_staff = request.POST.get("is_staff") == "true"
            user.is_superuser = request.POST.get("is_superuser") == "true"

            # Nếu nhập mật khẩu mới thì đổi luôn
            password = request.POST.get("password")
            if password:
                user.set_password(password)

            user.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect("users")

        # Nếu là tạo mới
        else:
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")

            is_active = request.POST.get("is_active") == "true"
            is_staff = request.POST.get("is_staff") == "true"
            is_superuser = request.POST.get("is_superuser") == "true"

            if password != password2:
                messages.error(request, "Passwords do not match.")
                return redirect("users")

            if User.objects.filter(username=username).exclude(email=email).exists():
                messages.error(request, "Username already exists.")
                return redirect("users")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect("users")

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_active = is_active
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()

            messages.success(request, f"User '{username}' created successfully.")
            return redirect("users")

    # GET → hiển thị danh sách
    users = User.objects.all().order_by("id")
    return render(request, "dashboard/users.html", {"users": users})


@login_required
def delete_user(request, user_id):
    # Lấy user cần xóa
    user_to_delete = get_object_or_404(User, id=user_id)

    # Chỉ admin mới xóa
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this user.")
        return redirect('users')

    # Không cho xóa chính mình
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('users')

    username = user_to_delete.username
    user_to_delete.delete()
    messages.success(request, f"User '{username}' has been deleted successfully.")
    return redirect('users')