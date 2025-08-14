from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('subcategory/<int:category_id>/', views.subcategory_detail, name='subcategory_detail'),
    path('blogcategory/<int:subcategory_id>/', views.category_blog, name='category_blog'),
]
