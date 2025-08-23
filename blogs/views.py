import requests
from django.shortcuts import render, get_object_or_404
from .models import Category, SubCategory, Blog
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import render


def home(request):
    categories = Category.objects.all()   # Lấy toàn bộ danh mục chính        
    subcategories = SubCategory.objects.all()  # Lấy toàn bộ danh mục con   
    featured_post = Blog.objects.filter(is_featured = True ,status = 'published' ) # Lấy các bài viết nổi bật (is_featured=True) và đã được xuất bản (status='published')
    posts = Blog.objects.filter(is_featured = False, status='published')  # Lấy các bài viết bình thường (không nổi bật) và đã xuất bản
    latest_posts = Blog.objects.order_by('-created_at')[:4]  # Lấy 5 bài mới nhất
    
        # --- Lấy dữ liệu YouTube channel ---
    api_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,brandingSettings,statistics",
        "id": "UC-jtWxHaKQX7UnG_fjoSZ-Q",  # ID kênh của bạn
        "key": "AIzaSyCB5g5djPGjEgWN2xjgmOvdNs861T4Vy18"  # API key
    }
    channel = None
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
        'posts': posts ,
        'channel': channel  # youtube
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
