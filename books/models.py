from django.db import models
from categories.models import Category
from django.contrib.auth.models import User
# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,  null=True, blank=True)
    
    l_user = models.ForeignKey(User, on_delete=models.CASCADE) 
    Price = models.FloatField( blank=True, null=True)  
    Available = models.IntegerField(default=0)  
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)

    def __str__(self):
        return self.title 
    class Meta:
        unique_together = ('title', 'category')
    
    def decrease_available(self):
        if self.Available > 0:
            self.Available -= 1
            self.save()


class Comment(models.Model):
    book= models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=30)
    email = models.EmailField()
    body = models. TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comments by {self.name}"
    


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username}'s Cart"

# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     def __str__(self):
#         return f"{self.book.title} - {self.quantity}"
from django.utils.timezone import now
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(blank=True, null=True)  # Automatically set from Book's Price
    timestamp = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if not self.price:  # Set the price only if it's not already set
            self.price = self.book.Price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.quantity} @ {self.price}"
