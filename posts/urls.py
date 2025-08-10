from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    HomeView,
    ContactView,
    PostDetailView,
    AddPostView,
    PostListView,
    PostUpdateView,
    PostDeleteView,
    PublishPostView,
    UnpublishPostView,
    PostsInCategoryView,
    PostsFreeListView,
    PostsPaidListView,
    CategoryListView,
    GetSubcategoriesView,
)


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacts/", ContactView.as_view(), name="contacts"),
    path("post_list/", PostListView.as_view(), name="post_list"),
    path('posts/free/', PostsFreeListView.as_view(), name='posts_free'),
    path('posts/paid/', PostsPaidListView.as_view(), name='posts_paid'),
    path("post/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("add_post/", AddPostView.as_view(), name="add_post"),
    path("edit/<int:pk>/", PostUpdateView.as_view(), name="post_edit"),
    path("delete/<int:pk>/", PostDeleteView.as_view(), name="post_delete"),
    path("posts/publish/<int:pk>/", PublishPostView.as_view(), name="publish_post"),
    path("posts/unpublish/<int:pk>/", UnpublishPostView.as_view(), name="unpublish_post"),
    path("category/<int:pk>/posts/", PostsInCategoryView.as_view(), name="posts_in_category"),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('subcategories/', GetSubcategoriesView.as_view(),  name='get_subcategories'),
]
