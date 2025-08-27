from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name = 'dashboard'),
    path('categories/', views.categories, name= 'categories'),
    path('subcategories/', views.subcategories, name= 'subcategories'),
    path('blogs/', views.blogs, name= 'blogs'),
    path('dashboard/subcategories/<int:sub_id>/', views.subcategory_detail, name='subcategories'),
    path('blogs/add/', views.add_blogs, name="add_blogs"),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('blogs/<int:blog_id>/edit/', views.edit_blogs, name="edit_blogs"),
    path('blogs/<int:blog_id>/delete/', views.delete_blogs, name="delete_blogs"),
    path('user/',views.users, name="users" ),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)