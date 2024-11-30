
from django.urls import path

from . import views

urlpatterns = [
    
    # path('', views.HomeView.as_view(), name='home'),
    path('homepage/', views.home, name='homepage'),
    path('category/<slug:category_slug>/', views.home, name='category_wise_book'),
]


# urlpatterns = [
    
#     path('home/', views.home, name='homepage'),
#     path('category/<slug:category_slug>/', views.home, name='category_wise_book'),
# ]