import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, SubCategory, Blog, Comment , Country ,ChildCategory, DetailCountry
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q,Case, When, Value, IntegerField
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

def home(request):
    import requests

    categories = Category.objects.prefetch_related(
        'subcategories__childcategories__detail_countries'
    ).order_by('created_at')

    subcategories = SubCategory.objects.all()
    featured_post = Blog.objects.filter(is_featured=True, status='published')
    posts = Blog.objects.filter(is_featured=False, status='published')
    latest_posts = Blog.objects.order_by('-created_at')[:4]

    # Lấy detail_country đầu tiên từ SubCategory thứ 2 của Category đầu tiên
    detail_country = None
    try:
        first_category = categories[0]
        second_subcategory = first_category.subcategories.all()[1]

        for child in second_subcategory.childcategories.all():
            if child.detail_countries.exists():
                detail_country = child.detail_countries.first()
                break
    except IndexError:
        detail_country = None

    # Lấy dữ liệu YouTube channel
    channel = None
    api_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,brandingSettings,statistics",
        "id": "UC-jtWxHaKQX7UnG_fjoSZ-Q",
        "key": "AIzaSyCB5g5djPGjEgWN2xjgmOvdNs861T4Vy18"
    }
    try:
        res = requests.get(api_url, params=params)
        data = res.json()
        if "items" in data and data["items"]:
            channel = data["items"][0]
    except Exception as e:
        print("Lỗi lấy dữ liệu YouTube:", e)

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'featured_post': featured_post,
        'latest_posts': latest_posts,
        'posts': posts,
        'channel': channel,
        'detail_country': detail_country,  # 👈 THÊM DỮ LIỆU NÀY
    }

    return render(request, 'home.html', context)



def get_youtube_channel():
    API_KEY = settings.YOUTUBE_API_KEY
    CHANNEL_ID = "UC-jtWxHaKQX7UnG_fjoSZ-Q"  # ID kênh YouTube

    base_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics,brandingSettings",
        "id": CHANNEL_ID,
        "key": API_KEY
    }
    res = requests.get(base_url, params=params)
    data = res.json()
    if "items" in data and len(data["items"]) > 0:
        return data["items"][0]
    return None

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id) # Lấy đối tượng Category từ database dựa trên category_id.
    subcategories = category.subcategories.all()   # Lấy tất cả các Subcategory liên quan đến Category vừa tìm được.
    
    # Trả về trang HTML 'category_detail.html' kèm theo dữ liệu context:
    #  - 'category': thông tin category hiện tại
    #  - 'subcategories': danh sách các subcategory thuộc category này
    return render(request, 'category_detail.html', {
        'category': category,
        'subcategories': subcategories
    })


def subcategory_detail(request, category_id):
    # Lấy category
    category = get_object_or_404(Category, id=category_id)
    
    # Lấy tất cả subcategories thuộc category này
    subcategories = category.subcategories.all()
    
    # Pagination cho subcategories
    paginator = Paginator(subcategories, 5)  # 5 sub mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'page_obj': page_obj,
    }
    return render(request, 'subcategory_detail.html', context)

def childcategory_detail(request, subcategory_id):
    # Lấy subcategory
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    # Lấy category cha
    category = subcategory.category

    # Lấy tất cả childcategories thuộc subcategory này
    childcategories = subcategory.childcategories.all()
    
    # Pagination cho childcategories (9 per page)
    from django.core.paginator import Paginator
    paginator = Paginator(childcategories, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'childcategory_detail.html', {
        'subcategory': subcategory,
        'category': category,  # thêm dòng này
        'childcategories': childcategories,
        'page_obj': page_obj,
    })

def country_detail(request, pk):
    country = get_object_or_404(Country, pk=pk)
    # Lấy tất cả DetailCountry thuộc ChildCategory của Country
    detailcountries = country.childcategory.detail_countries.all()

    context = {
        'country': country,
        'detailcountries': detailcountries
    }
    return render(request, 'country_detail.html', context)


def detailcountry_detail(request, childcategory_id):
    # Lấy ChildCategory
    childcategory = get_object_or_404(ChildCategory, id=childcategory_id)

    # Lấy tất cả DetailCountry thuộc ChildCategory này
    detailcountries = childcategory.detail_countries.all()  # dùng related_name

    context = {
        'childcategory': childcategory,
        'detailcountries': detailcountries,
    }
    return render(request, 'country_detail.html', context)


# views.py
def category_blog(request, detailcountry_id):
    detail = get_object_or_404(DetailCountry, id=detailcountry_id)
    childcategory = detail.childcategory
    subcategory = childcategory.subcategory
    category = subcategory.category

    blogs = Blog.objects.filter(detail_country=detail, status='published').order_by('-created_at')
    featured_post = Blog.objects.filter(is_featured=True, status='published')

    return render(request, 'category_blog.html', {
        'detail': detail,
        'childcategory': childcategory,
        'subcategory': subcategory,
        'category': category,
        'blogs': blogs,
        'featured_post': featured_post,
    })



def youtube_info(request):
    api_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,brandingSettings,statistics",
        "id": "UC-jtWxHaKQX7UnG_fjoSZ-Q",
        "key": "AIzaSyCB5g5djPGjEgWN2xjgmOvdNs861T4Vy18"
    }
    res = requests.get(api_url, params=params)
    data = res.json()

    channel = None
    if "items" in data and len(data["items"]) > 0:
        channel = data["items"][0]

    return render(request, "base/youtube_info.html", {
        "channel": channel
    })


def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # 🟢 Lấy detailcountry, childcategory, subcategory, category để breadcrumb
    detailcountry = getattr(blog, "detail_country", None)
    childcategory = getattr(detailcountry, "childcategory", None) if detailcountry else None
    subcategory = getattr(childcategory, "subcategory", None) if childcategory else None
    category = getattr(subcategory, "category", None) if subcategory else None

    # Lấy blog liên quan (lọc theo detail_country)
    related_blogs = Blog.objects.filter(
        detail_country=blog.detail_country
    ).exclude(id=blog.id).order_by('-created_at')[:4]
    if not related_blogs.exists():
        related_blogs = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:4]

    # Xử lý POST: thêm comment hoặc xóa comment
    if request.method == "POST":
        if 'delete_comment_id' in request.POST and request.user.is_superuser:
            comment_id = request.POST.get('delete_comment_id')
            comment_to_delete = get_object_or_404(Comment, id=comment_id)
            comment_to_delete.delete()
            messages.success(request, "Comment đã được xóa!")
            return redirect(f'/blog/{blog_id}/')

        elif request.user.is_authenticated:
            if request.user.is_active:
                content = request.POST.get("comment")
                if content:
                    Comment.objects.create(blog=blog, user=request.user, content=content)
                    messages.success(request, "Bình luận của bạn đã được gửi!")
                else:
                    messages.error(request, "Bình luận không được để trống!")
            else:
                messages.warning(request, "Tài khoản chưa active, không thể bình luận.")
            return redirect(f'/blog/{blog_id}/')

    # Lấy comment với pagination
    comment_list = Comment.objects.filter(blog=blog).order_by('-created_at')
    paginator = Paginator(comment_list, 5)
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'related_blogs': related_blogs,
        'comments': comments,
        'detailcountry': detailcountry,
        'childcategory': childcategory,
        'subcategory': subcategory,
        'category': category,
    })


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    blogs = Blog.objects.none()

    if keyword:
        # Tách từ khóa theo khoảng trắng
        words = keyword.split()

        # Build Q object cho từng từ
        query = Q()
        for word in words:
            query |= Q(title__icontains=word)
            query |= Q(short_description__icontains=word)
            query |= Q(blog_body__icontains=word)

        # Filter theo status
        blogs = Blog.objects.filter(query, status='published').distinct()

        # Sắp xếp theo mức độ liên quan: title match trước
        blogs = blogs.annotate(
            relevance=Case(
                When(title__icontains=keyword, then=Value(3)),
                When(short_description__icontains=keyword, then=Value(2)),
                When(blog_body__icontains=keyword, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-relevance', '-id')

    # Pagination: 9 bài / trang
    paginator = Paginator(blogs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'blogs': page_obj.object_list,  # chỉ các blog trên trang hiện tại
        'keyword': keyword,
        'page_obj': page_obj,           # cần cho template pagination
    }
    return render(request, 'search.html', context)

def auth_action(request):
    """
    Xử lý đăng nhập, đăng ký, đăng xuất chung qua action POST
    """
    if request.method == "POST":
        action = request.POST.get("action")

        # Logout
        if action == "logout":
            logout(request)
            messages.success(request, "Đăng xuất thành công!")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Login
        elif action == "login":
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Chào mừng {user.username}!")
            else:
                messages.error(request, "Sai tài khoản hoặc mật khẩu!")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Register
        elif action == "register":
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()
            confirm_password = request.POST.get("confirmPassword", "").strip()

            if not username or not email or not password or not confirm_password:
                messages.error(request, "Vui lòng điền đầy đủ thông tin.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            if len(username) > 10:
                messages.error(request, "Tài khoản tối đa 10 ký tự.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            if password != confirm_password:
                messages.error(request, "Mật khẩu không khớp.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            if User.objects.filter(username=username).exists():
                messages.error(request, "Tài khoản đã tồn tại.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email đã được sử dụng.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Đăng ký thành công! Bạn có thể đăng nhập ngay.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

    # Nếu GET request, chỉ render trang bình thường
    return redirect('home')

@login_required
def post_comment(request, post_id):
    post = get_object_or_404(Blog, id=post_id)

    if not request.user.is_active:
        messages.error(request, "Tài khoản của bạn chưa active, không thể bình luận.")
        return redirect(post.get_absolute_url())

    if request.method == "POST":
        content = request.POST.get("comment")
        if content:
            label = "Quản trị viên" if request.user.is_superuser else ""
            Comment.objects.create(
                blog=post,
                user=request.user,
                content=content,
                label=label
            )
            messages.success(request, "Bình luận của bạn đã được gửi!")
        else:
            messages.error(request, "Bình luận không được để trống!")

    return redirect(post.get_absolute_url())