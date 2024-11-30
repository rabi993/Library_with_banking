from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class HomeView(TemplateView):
    template_name = 'index.html'


from books.models import Book
from categories.models import Category
def home(request,category_slug = None):
    data = Book.objects.all()
    if category_slug is not None:
        category = Category.objects.get(slug= category_slug)
        data = Book.objects.filter(category = category) 
    categories = Category.objects.all()
    return render(request, 'home.html', {'data' : data, 'category': categories} ) 