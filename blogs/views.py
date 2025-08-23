import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, SubCategory, Blog
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q,Case, When, Value, IntegerField
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def home(request):
    # --- Lấy dữ liệu cho trang ---
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    featured_post = Blog.objects.filter(is_featured=True, status='published')
    posts = Blog.objects.filter(is_featured=False, status='published')
    latest_posts = Blog.objects.order_by('-created_at')[:4]

    # --- Lấy dữ liệu YouTube channel ---
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
    category = get_object_or_404(Category, id=category_id)
    subcategories = category.subcategories.all()
    blogs = Blog.objects.filter( subcategory__in=subcategories,status='published') 
    
    # Pagination cho subcategories
    paginator = Paginator(subcategories, 5)  # 5 sub mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    # Bài nổi bật
    featured_post = Blog.objects.filter(is_featured=True, status='published')
    return render(request, 'subcategory_detail.html', {
        'category': category,
        'subcategories': subcategories,
        'page_obj': page_obj, 
        'blogs': blogs,
        'featured_post': featured_post,
    })

def category_blog(request, subcategory_id):
    # Lấy đúng subcategory theo id
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    # Lấy category cha của subcategory này
    category = subcategory.category  
    # Lấy blog thuộc subcategory này
    blogs = Blog.objects.filter(subcategory=subcategory,status='published').order_by('-created_at')
    # Bài viết nổi bật (toàn bộ site hoặc chỉ subcategory này tùy ý)
    featured_post = Blog.objects.filter(is_featured=True, status='published')

    return render(request, 'category_blog.html', {
        'category': category,
        'subcategory': subcategory,
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
    subcategory = blog.subcategory           # đây là SubCategory của blog
    category = subcategory.category          # đây là Category cha
    
    related_blogs = Blog.objects.filter(subcategory=blog.subcategory).exclude(id=blog.id).order_by('-created_at')[:4]
    if not related_blogs.exists():
        related_blogs = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:4]
        
    return render(request, 'blog_detail.html', {
        'blog': blog,
        'subcategory': subcategory,
        'category': category,
        'related_blogs': related_blogs,
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