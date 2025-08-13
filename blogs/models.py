from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)  
    short_description = models.TextField(max_length=1000, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return f"{self.category} - {self.name}"


STATUS_CHOICE = (
    ('draft', 'Draft'),
    ('published', 'Published')
)

class Blog(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)  
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_image = models.ImageField(upload_to='uploads/%y/%m/%d')
    short_description = models.TextField(max_length=1000)
    blog_body = CKEditor5Field('Description', config_name='default')  
    status = models.CharField(max_length=100, choices=STATUS_CHOICE, default='draft')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Blogs'

    def __str__(self):
        return self.title

