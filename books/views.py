from django.shortcuts import render, redirect,get_object_or_404
from . import forms
from . import models
from django.contrib.auth.decorators import login_required
from .models import Book, Cart, CartItem

from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
# Create your views here.

@login_required
def add_book(request):
    if request.method =='POST':
        book_form = forms.BookForm(request.POST)
        if book_form.is_valid():
            book_form.instance.l_user = request.user
            book_form.save()
            return redirect('homepage')
    else:
        book_form = forms.BookForm()

    return render(request, 'add_book.html', {'form': book_form})

# Add book using Class based view
@method_decorator(login_required, name='dispatch')
class AddBookCreateView(CreateView):
    model = models.Book
    form_class= forms.BookForm
    template_name= 'add_book.html'
    # success_url= reverse_lazy('add_book')
    success_url= reverse_lazy('homepage')
    def form_valid(self, form): 
        form.instance.l_user = self.request.user
        return super().form_valid(form)



@login_required
def edit_book(request, id):
    book = models.Book.objects.get(pk=id)
    book_form = forms.BookForm(instance=book)
    # print(book.title)
    if request.method =='POST':
        book_form = forms.BookForm(request.POST, instance=book)
        if book_form.is_valid():
            book_form.instance.l_user = request.user
            book_form.save()
            return redirect('homepage')
    # else:
    #     book_form = forms.BookForm()

    return render(request, 'add_book.html', {'form': book_form})

# Edit book using class based view
@method_decorator(login_required, name='dispatch')
class EditBookView(UpdateView):
    model = models.Book
    form_class = forms.BookForm
    template_name ='add_book.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('profile')




@login_required
def delete_book(request, id):
    book = models.Book.objects.get(pk=id)
    book.delete()
    return redirect('homepage')

# delete book using class based view
@method_decorator(login_required, name='dispatch')
class DeleteBookView(DeleteView):
    model = models.Book
    template_name ='delete.html'
    success_url = reverse_lazy('profile')
    pk_url_kwarg = 'id'

class DetailBookView(DetailView):
    model = models.Book
    # pk_url_kwarg='id'
    template_name = 'book_details.html'


    def post(self, request, *args, **kwargs):
        comment_form= forms.CommentForm(data=self.request.POST)
        post = self.get_object()
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.book = post
            new_comment.save()
        return self.get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = post.comments.all()
        comment_form = forms.CommentForm()
        
        context['comments'] = comments
        context['comment_form'] = comment_form
        return context

from decimal import Decimal
from transactions.constants import BORROW_BOOK
from transactions.models import Transaction  # Import the transaction model and type

def borrow_now(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Ensure the user has enough balance
    user_account = request.user.account
    if book.Available > 0:
        if user_account.balance >= Decimal(str(book.Price)):  # Convert book price to Decimal
            # Deduct the price of the book from the user's account balance
            user_account.balance -= Decimal(str(book.Price))
            user_account.save()

            # Record the transaction with type `BORROW_BOOK`
            Transaction.objects.create(
                account=user_account,
                amount=Decimal(str(book.Price)),
                transaction_type=BORROW_BOOK,
                balance_after_transaction=user_account.balance
            )

            # Decrease book availability
            book.decrease_available()

            # Get or create a cart for the user
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Check if item is already in the cart
            cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

            if created:
                # If a new item is added, set its price
                cart_item.price = book.Price
            else:
                # If the item already exists, increment quantity
                cart_item.quantity += 1

            # Save the updated cart item
            cart_item.save()

            messages.success(request, "book purchased successfully!")
        else:
            messages.error(request, "Insufficient balance to borrow this book.")
    else:
        messages.error(request, "book is not available.")

    return redirect('detail_book', pk=book.id)
