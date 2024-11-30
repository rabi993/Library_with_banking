from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import login, logout,update_session_auth_hash, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import redirect
from transactions.views import send_transaction_email

from books.models import Book, Cart
from categories.models import Category
# import logging

class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self,form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        print(user)
        return super().form_valid(form) # form_valid function call hobe jodi sob thik thake
    
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')


# logger = logging.getLogger(__name__)
# class UserLogoutView(LogoutView):
#     # next_page = reverse_lazy('home')
#     def get_success_url(self):
#         if self.request.user.is_authenticated:
#             logout(self.request)
#         return reverse_lazy('home')
#     # def dispatch(self, request, *args, **kwargs):
#     #     logger.info("LogoutView accessed")
#     #     return super().dispatch(request, *args, **kwargs)

def user_logout(request):
    logout(request)
    return redirect('login')


# class UserBankAccountUpdateView(View):
#     template_name = 'accounts/profile.html'

#     def get(self, request):
#         form = UserUpdateForm(instance=request.user)
#         return render(request, self.template_name, {'form': form})

#     def post(self, request):
#         form = UserUpdateForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('profile')  # Redirect to the user's profile page
#         return render(request, self.template_name, {'form': form})
    

# def Profile(request,category_slug = None):
#     data = Book.objects.filter(l_user= request.user)
#     if category_slug is not None:
#         category = Category.objects.get(slug= category_slug)
#         data = Book.objects.filter(l_user= request.user, category = category) 
#     categories = Category.objects.all()
#     cart = Cart.objects.filter(user=request.user).first()
    
    
#     return render(request, 'profile.html', {'data': data, 'category': categories, 'cart': cart})

class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request, category_slug=None):
        form = UserUpdateForm(instance=request.user)
        data = Book.objects.filter(l_user=request.user)
        if category_slug is not None:
            category = Category.objects.get(slug=category_slug)
            data = Book.objects.filter(l_user=request.user, category=category)
        categories = Category.objects.all()
        cart = Cart.objects.filter(user=request.user).first()
        account_balance = request.user.account.balance # Fetch the account balance

        context = {
            'form': form,
            'data': data,
            'category': categories,
            'cart': cart,
            'account_balance': account_balance,  # Pass balance to template
            # 'cart_items': cart.items.all() if cart else [],
        }
        return render(request, self.template_name, context)

    def post(self, request, category_slug=None):
        form = UserUpdateForm(request.POST, instance=request.user)
        data = Book.objects.filter(l_user=request.user)
        categories = Category.objects.all()
        cart = Cart.objects.filter(user=request.user).first()
        account_balance = request.user.account.balance  # Fetch the account balance

        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after successful update

        context = {
            'form': form,
            'data': data,
            'category': categories,
            'cart': cart,
            'account_balance': account_balance,  # Pass balance to template
        }
        return render(request, self.template_name, context)
    # def post(self, request, category_slug=None):
    #     form = UserUpdateForm(request.POST, instance=request.user)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('profile')  # Redirect to profile page
    #     return self.get(request, category_slug)



def pass_change(request):
    if request.method =='POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password updated Successfully')
            update_session_auth_hash(request, form.user)
            send_transaction_email(request.user, 0, "Password Changed", "accounts/pass_change_email.html")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/pass_change.html', {'form': form})
    

from .models import BorrowItem

@login_required
def borrow_list(request):
    user_items = BorrowItem.objects.filter(user=request.user)
    
    return render(request, 'accounts/borrow_list.html', {'user_items': user_items})

# def borrow_list(request, book_id):
#     book = get_object_or_404(Book, id=book_id)
#     # You can handle the logic for adding the book to the user's borrow list here
#     return render(request, 'borrow_list.html', {'book': book})



from decimal import Decimal
from transactions.constants import RETURN_BOOK
from transactions.models import Transaction
from books.models import CartItem

def return_item(request, cart_item_id):
    # Fetch the cart item
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    # Increase the book's available quantity
    book = cart_item.book
    book.Available += cart_item.quantity
    book.save()

    # Calculate the total price of the returned item
    total_price = Decimal(str(cart_item.price)) * cart_item.quantity

    # Add the amount back to the user's account
    user_account = request.user.account
    user_account.balance += total_price
    user_account.save()

    # Record the transaction with type `RETURN_BOOK`
    Transaction.objects.create(
        account=user_account,
        amount=total_price,
        transaction_type=RETURN_BOOK,
        balance_after_transaction=user_account.balance
    )

    # Delete the cart item
    cart_item.delete()

    # Notify the user
    messages.success(request, "Item returned successfully. The amount has been added to your account.")
    
    return redirect('profile')  # Redirect to the user's profile page
