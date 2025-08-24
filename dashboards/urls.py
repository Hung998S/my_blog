from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name = 'dashboard'),
    path('categories/', views.categories, name= 'categories'),
    path('subcategories/', views.subcategories, name= 'subcategories'),
    path('blogs/', views.blogs, name= 'blogs'),
    path('dashboard/subcategories/<int:sub_id>/', views.subcategory_detail, name='subcategories'),

    ]
