from django.contrib import admin
from .models import UserBankAccount, UserAddress, BorrowItem, Product
# Register your models here.

admin.site.register(UserBankAccount)
admin.site.register(UserAddress)
admin.site.register(BorrowItem)
admin.site.register(Product)

