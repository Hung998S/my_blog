from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
from django.core.validators import FileExtensionValidator

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    icon = models.FileField(
        upload_to='category_icons/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=50, unique=True)
    icon = models.FileField(
        upload_to='subcategory_icons/',
        blank=True,
        null=True
    )

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

class ChildCategory(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='childcategories')
    title = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='childcategory_images/', blank=True, null=True)
    short_description = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'ChildCategories'

    def __str__(self):
        return f"{self.subcategory} - {self.title}"


class Country(models.Model):
    # Liên kết với ChildCategory
    childcategory = models.ForeignKey(
        ChildCategory,
        on_delete=models.CASCADE,
        related_name='countries',
        verbose_name="Nhóm con"
    )

    name = models.CharField(max_length=100, unique=True, verbose_name="Tên quốc gia")
    capital = models.CharField(max_length=100, verbose_name="Thủ đô")
    flag = models.ImageField(
        upload_to='flags/',
        blank=True,
        null=True,
        verbose_name="Quốc kỳ"
    )
    
    map = models.ImageField(
    upload_to='maps/',
    blank=True,
    null=True,
    verbose_name="Bản đồ"
)

    # CKEditor5Field cho nội dung dạng đoạn văn có định dạng
    geography = CKEditor5Field('Vị trí địa lý', config_name='default', blank=True, null=True)
    area = CKEditor5Field('Diện tích', config_name='default', blank=True)
    population = CKEditor5Field('Dân số', config_name='default', blank=True)
    language = CKEditor5Field('Ngôn ngữ chính', config_name='default', blank=True)
    government = CKEditor5Field('Chính thể', config_name='default', blank=True)
    economy = CKEditor5Field('Kinh tế', config_name='default', blank=True)
    currency = CKEditor5Field('Tiền tệ', config_name='default', blank=True)
    climate = CKEditor5Field('Khí hậu', config_name='default', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("country_detail", kwargs={"pk": self.pk})






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
    
    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.id])


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=250)
    label = models.CharField(max_length=20, blank=True)  # nhãn: "Quản trị viên" nếu superuser
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} ({self.label}) - {self.blog.title[:20]}: {self.content[:30]}'
