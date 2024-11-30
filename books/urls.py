from django.contrib import admin
from django.urls import path, include
from . import views
# from transactions.views import BorrowBookView
urlpatterns = [
    # path('add/', views.add_book, name='add_book'),
    path('add/', views.AddBookCreateView.as_view(), name='add_book'),
    # path('edit/<int:id>', views.edit_book, name='edit_book'),
    path('edit/<int:id>', views.EditBookView.as_view(), name='edit_book'),
    # path('delete/<int:id>', views.delete_book, name='delete_book'),
    path('delete/<int:id>', views.DeleteBookView.as_view(), name='delete_book'),
    path('books/details/<int:pk>', views.DetailBookView.as_view(), name='detail_book'),
    path('books/borrow/<int:book_id>/', views.borrow_now, name='borrow_now'),
    
    # path('borrow-book/<int:book_id>/', borrowBookView.as_view(), name='borrow_book'),
    
   
]