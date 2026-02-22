from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostListView.as_view(), name='list-posts'),
    path("post/create/", views.post_create_view, name="post_create"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/<slug:slug>/edit/", views.post_detail_update_view, name="post_detail_update"),
    path("category/<slug:slug>/", views.CategoryPostListView.as_view(), name='category_posts'),
    path("search/", views.SearchResultsListView.as_view(), name='search_results'),

    # Account related urls
    path('account/profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('account/profile/edit/', views.profile_edit, name='profile_edit'),
    path("account/login/", views.login_view, name='login'),
    path("account/logout/", views.logout_view, name='logout'),
    path("account/register/", views.register, name='register'),
]