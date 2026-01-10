from django.contrib import admin
from .models import Post, Category, Comment, Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 1. Which columns to show in the list view
    list_display = ('title', 'author', 'status', 'created_at', 'published_at')
    
    # 2. Side-bar filters (Very useful as data grows)
    list_filter = ('status', 'created_at', 'author', 'categories')
    
    # 3. Search functionality (SQL LIKE queries)
    search_fields = ('title', 'body')
    
    # 4. Automatic slug generation
    prepopulated_fields = {'slug': ('title',)}
    
    # 5. UI for Many-to-Many categories
    filter_horizontal = ('categories',)
    
    # 6. Make status editable directly from the list page
    list_editable = ('status',)
    
    # 7. Organize fields into sections in the edit form
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'body', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('status', 'categories', 'published_at')
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    # Automatically creates the slug as you type the category name
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Helps you moderate by showing the most important info at a glance
    list_display = ('author', 'post', 'created_at', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('author__username', 'body')
    # Allows you to toggle a comment's visibility without leaving the list view
    list_editable = ('active',)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Info'

# Now define a new UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)