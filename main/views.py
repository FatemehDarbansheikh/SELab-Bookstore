from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.auth.views import LoginView, LogoutView

from .models import (
    Book, Category, Cart, Wishlist,
    Order, OrderItem, Address, Review
)

def home_view(request):
    books = Book.objects.all().order_by('-id')[:8]
    return render(request, 'pages/home.html', {'books': books})


def book_list_view(request):
    books = Book.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(categories__id=category_id)

    context = {
        'books': books,
        'categories': categories
    }
    return render(request, 'pages/book_list.html', context)


def book_detail_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book)

    return render(request, 'pages/book_detail.html', {
        'book': book,
        'reviews': reviews
    })


@login_required
def add_to_cart_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, 'کتاب به سبد خرید اضافه شد')
    return redirect('cart')


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_price = sum(
        item.book.price * item.quantity
        for item in cart_items
    )

    return render(request, 'pages/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def remove_from_cart_view(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    messages.info(request, 'آیتم حذف شد')
    return redirect('cart')


@login_required
def add_to_wishlist_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    messages.success(request, 'به علاقه‌مندی‌ها اضافه شد')
    return redirect('wishlist')


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'pages/wishlist.html', {'items': items})


@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    address = Address.objects.filter(user=request.user, is_default=True).first()

    if not cart_items or not address:
        messages.error(request, 'سبد خرید یا آدرس معتبر نیست')
        return redirect('cart')

    total_amount = sum(
        item.book.price * item.quantity
        for item in cart_items
    )

    order = Order.objects.create(
        user=request.user,
        address=address,
        total_amount=total_amount,
        status='pending'
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            book=item.book,
            quantity=item.quantity,
            unit_price=item.book.price
        )

    cart_items.delete()
    messages.success(request, 'سفارش ثبت شد')
    return redirect('orders')


@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'pages/orders.html', {'orders': orders})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'main/auth/signup.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'main/auth/login.html'


class CustomLogoutView(LogoutView):
    pass
