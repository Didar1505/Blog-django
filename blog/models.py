from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django.templatetags.static import static

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/%Y/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    social_twitter = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    @property
    def get_avatar_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return static("images/default-avatar.jpg")

class Category(models.Model):
    COLORS = [
        ('primary', 'primary'),
        ('secondary', 'secondary'),
        ('success', 'success'),
        ('danger', 'danger'),
        ('warning', 'warning'),
        ('info', 'info'),
        ('dark', 'dark'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, choices=COLORS, default='primary')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return str(self.name)

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'

    categories = models.ManyToManyField(Category, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = CKEditor5Field("Text", config_name='extends')
    featured_image = models.ImageField(upload_to='%Y/%m/%d/',null=True, blank=True)
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.title)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
