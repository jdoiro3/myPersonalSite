from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='blog-index'),
    path('cat/<str:category>/', views.index, name='index-specific-cat'),
    path('author/<str:author_first_name>-<str:author_last_name>/', views.author_index, name='specific-author'),
    path('post/<slug:slug>/', views.post_detail, name='post-detail'),
    path('edit/', views.new_post, name='new-post'),
    path('edit/<str:Id>/', views.post_editor, name='post-edit')
]