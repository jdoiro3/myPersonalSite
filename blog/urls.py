from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:category>/', views.index, name='index-specific-cat'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
]