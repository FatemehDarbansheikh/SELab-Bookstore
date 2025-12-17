from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg

from .models import (
    User, Book, Category, Author, Cart, Wishlist,
    Order, OrderItem, Address, Review
)


def home_view(request):
    books = Book.objects.all().order_by('-id')[:8]
    categories = Category.objects.all()

    return render(request, 'main/home.html', {
        'books': books,
        'categories': categories
    })


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        login(request, user)
        return redirect('home')

    return render(request, 'main/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')

    return render(request, 'main/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def book_list_view(request):
    books = Book.objects.all()

    query = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort')

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__first_name__icontains=query) |
            Q(authors__last_name__icontains=query)
        ).distinct()

    if category:
        books = books.filter(categories__id=category)

    if sort == 'price_low':
        books = books.order_by('price')
    elif sort == 'price_high':
        books = books.order_by('-price')

    categories = Category.objects.all()

    return render(request, 'main/book_list.html', {
        'books': books,
        'categories': categories
    })


def book_detail_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'main/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'avg_rating': avg_rating
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

    return redirect('cart')


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_price = sum(
        item.book.price * item.quantity for item in cart_items
    )

    return render(request, 'main/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def remove_from_cart_view(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'main/wishlist.html', {'items': items})


@login_required
def add_to_wishlist_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    return redirect('wishlist')


@login_required
def remove_from_wishlist_view(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    return redirect('wishlist')


@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        address_id = request.POST['address']
        address = get_object_or_404(Address, id=address_id)

        total = sum(item.book.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total,
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
        return redirect('order_detail', order.id)

    return render(request, 'main/checkout.html', {
        'cart_items': cart_items,
        'addresses': addresses
    })


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'main/order_detail.html', {
        'order': order,
        'items': items
    })


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'main/order_history.html', {'orders': orders})


@login_required
def add_review_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST.get('comment')

        Review.objects.create(
            user=request.user,
            book=book,
            rating=rating,
            comment=comment
        )

        return redirect('book_detail', book_id)

    return render(request, 'main/add_review.html', {'book': book})
