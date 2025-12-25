from django.contrib import admin
from .models import (
    User, Admin, Address, Publisher, Author, Category, Book,
    Review, Cart, Wishlist, Order, OrderItem, Payment, Support, Notification
)

admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Address)
admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Support)
admin.site.register(Notification)

