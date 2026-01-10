from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.utils.text import slugify

from . import models, forms

def index(request):
    return HttpResponse("Hello world")

class PostListView(ListView):
    model = models.Post
    template_name = 'blog/posts.html'
    context_object_name = 'blogs'
    paginate_by = 5

    def get_queryset(self):
        return (
            models.Post.objects
            .filter(status=models.Post.Status.PUBLISHED)
            .select_related('author')
            .prefetch_related('categories')
            .order_by('-published_at')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = models.Category.objects.all()
        return context

class PostDetailView(DetailView):
    model = models.Post
    template_name = 'blog/post-detail.html'
    slug_url_kwarg = 'slug'
    query_pk_and_slug = True
    context_object_name = 'post'

    def get_queryset(self):
        return models.Post.objects.filter(status=models.Post.Status.PUBLISHED).select_related("author")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(
            active=True, parent__isnull=True
        ).prefetch_related("replies__author", "author")
        context['comment_form'] = forms.CommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in to comment.'}, status=401)

        self.object = self.get_object()
        form = forms.CommentForm(request.POST)

        if form.is_valid():
            # 2. commit=False allows us to add hidden data (author/post)
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            
            # 3. Handle Nesting: Is this a reply?
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(models.Comment, id=parent_id)
                # Wisdom: Flatten nesting (if parent has a parent, use the grandparent)
                comment.parent = parent_comment.parent if parent_comment.parent else parent_comment
            
            comment.save()

            # 4. Render the partial HTML to send back to JS
            comment_html = render_to_string(
                'blog/partials/_comment.html', 
                {'comment': comment}, 
                request=request
            )

            return JsonResponse({
                'success': True,
                'comment_html': comment_html,
                'message': 'Comment posted successfully!'
            })

        # 5. Handle Form Errors
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
class CategoryPostListView(ListView):
    model = models.Post
    template_name = "blog/posts.html"
    paginate_by = 5
    context_object_name = "blogs"

    def get_queryset(self):
        self.category = get_object_or_404(models.Category, slug=self.kwargs['slug'])
        return(
            models.Post.objects.filter(status=models.Post.Status.PUBLISHED, categories=self.category)
            .select_related('author')
            .prefetch_related('categories')
            .order_by('-published_at')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = models.Category.objects.all()

        return context

class SearchResultsListView(ListView):
    model = models.Post
    template_name = 'blog/posts.html'
    context_object_name = 'blogs'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return models.Post.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query),
                status=models.Post.Status.PUBLISHED
            ).distinct()
        return models.Post.objects.none()

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = models.Profile
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile

    # override the return context to the rendering page
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_posts'] = models.Post.objects.filter(author=self.request.user).order_by('-created_at')
        return context

def register(request):
    if request.user.is_authenticated:
        return redirect('profile_detail')

    if request.method == "POST":
        form = forms.UserRegistrationForm(request.POST)
        
        # 1. Check if the passwords match manually (extra safety for manual HTML forms)
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        
        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'blog/register.html')

        # 2. Check if the Django form is valid
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to the club, {user.username}!")
            return redirect('profile_detail')
        else:
            # 3. If the form is invalid, send the errors to the template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    return render(request, 'blog/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile_detail')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile_detail')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "blog/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile_edit(request):
    profile = request.user.profile

    if request.method == "POST":
        u_form = forms.UserUpdateForm(request.POST, instance=request.user)
        p_form = forms.ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("profile_detail")
        else:
            print(u_form.errors)
            print(p_form.errors)

    else:
        u_form = forms.UserUpdateForm(instance=request.user)
        p_form = forms.ProfileUpdateForm(instance=profile)

    context = {"u_form": u_form, "p_form": p_form, "profile":profile}
    return render(request, 'blog/profile_edit.html', context)

@login_required
def post_detail_update_view(request, slug):
    post = get_object_or_404(models.Post, slug=slug)
    if post.author != request.user:
        return redirect('list-posts')
    
    if request.method == "POST":
        form = forms.CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_detail", slug=post.slug)
    else:
        form = forms.CreatePostForm(instance=post)
    
    return render(request, 'blog/post_create.html', {"form": form})

class PostCreateView(LoginRequiredMixin, CreateView):
    model = models.Post
    form_class = forms.CreatePostForm
    template_name = 'blog/post_create.html'
    login_url = "/account/login/"

    def form_valid(self, form):
        print(form.errors) # This will print the errors in your terminal/server log
        # Automatically set the author to the logged-in user
        form.instance.author = self.request.user
        # Automatically generate a slug from the title
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', kwargs={'slug': self.object.slug})
    
@login_required
def post_create_view(request):
    if request.method == "POST":
        form = forms.CreatePostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  
            if not post.slug:
                post.slug = slugify(post.title)
            post.save()
            form.save_m2m()
            return redirect('post_detail', slug=post.slug)
        else:
            print(form.errors)    
    else:
        form = forms.CreatePostForm()
    return render(request, 'blog/post_create.html', {"form": form})