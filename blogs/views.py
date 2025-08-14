from django.shortcuts import render, get_object_or_404
from .models import Category, SubCategory, Blog
from django.core.paginator import Paginator


def home(request):
    categories = Category.objects.all()   # Lấy toàn bộ danh mục chính        
    subcategories = SubCategory.objects.all()  # Lấy toàn bộ danh mục con   
    featured_post = Blog.objects.filter(is_featured = True ,status = 'published' ) # Lấy các bài viết nổi bật (is_featured=True) và đã được xuất bản (status='published')
    posts = Blog.objects.filter(is_featured = False, status='published')  # Lấy các bài viết bình thường (không nổi bật) và đã xuất bản
    latest_posts = Blog.objects.order_by('-created_at')[:6]  # Lấy 5 bài mới nhất

    context = {
        'categories': categories,
        'subcategories': subcategories,      
        'featured_post': featured_post,
        'latest_posts': latest_posts,
        'posts': posts 
    }

    return render(request, 'home.html', context)

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
    blogs = Blog.objects.filter(subcategory=subcategory,status='published')
    # Bài viết nổi bật (toàn bộ site hoặc chỉ subcategory này tùy ý)
    featured_post = Blog.objects.filter(is_featured=True, status='published')

    return render(request, 'category_blog.html', {
        'category': category,
        'subcategory': subcategory,
        'blogs': blogs,
        'featured_post': featured_post,
    })



