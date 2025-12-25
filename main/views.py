from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from .forms import AddressForm

from .models import (
    User, Address, Category, Book,
    Review, Cart, Wishlist,
    Order, OrderItem, Payment,
    Notification, Support
)
from .forms import EditProfileForm, SupportForm
from .utils import send_notification_email


def home_view(request):
    books = Book.objects.all().order_by('-id')[:8]
    categories = Category.objects.all()
    return render(request, 'main/home.html', {
        'books': books,
        'categories': categories
    })


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً استفاده شده است.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'این ایمیل قبلاً ثبت شده است.')
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
        login(request, user)
        return redirect('home')

    return render(request, 'main/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, 'با موفقیت وارد شدید.')
            return redirect('home')

        messages.error(request, 'نام کاربری یا رمز عبور نادرست است.')

    return render(request, 'main/login.html')



@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def book_list_view(request):
    books = Book.objects.all()
    q = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort')

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(authors__first_name__icontains=q) |
            Q(authors__last_name__icontains=q)
        ).distinct()

    if category:
        books = books.filter(categories__id=category)

    if sort == 'price_low':
        books = books.order_by('price')
    elif sort == 'price_high':
        books = books.order_by('-price')

    return render(request, 'main/book_list.html', {
        'books': books,
        'categories': Category.objects.all()
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
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        book_id=book_id,
        defaults={'quantity': 1}
    )
    if not created:
        cart.quantity += 1
        cart.save()
    return redirect('cart')


@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(i.book.price * i.quantity for i in items)
    return render(request, 'main/cart.html', {
        'cart_items': items,
        'total_price': total
    })


@login_required
def update_cart_quantity(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease':
        item.quantity -= 1

    if item.quantity <= 0:
        item.delete()
    else:
        item.save()

    return redirect('cart')


@login_required
def remove_from_cart_view(request, item_id):
    get_object_or_404(Cart, id=item_id, user=request.user).delete()
    return redirect('cart')


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'main/wishlist.html', {'items': items})


@login_required
def add_to_wishlist_view(request, book_id):
    Wishlist.objects.get_or_create(user=request.user, book_id=book_id)
    return redirect('wishlist')


@login_required
def remove_from_wishlist_view(request, item_id):
    get_object_or_404(Wishlist, id=item_id, user=request.user).delete()
    return redirect('wishlist')


@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, 'سبد خرید خالی است')
        return redirect('cart')

    if request.method == 'POST':
        address = get_object_or_404(Address, id=request.POST['address'], user=request.user)
        total = sum(i.book.price * i.quantity for i in cart_items)

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
        return redirect('online_payment', order.id)

    return render(request, 'main/checkout.html', {
        'cart_items': cart_items,
        'addresses': Address.objects.filter(user=request.user)
    })


@login_required
def online_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        Payment.objects.create(
            order=order,
            payment_method='Online',
            amount=order.total_amount,
            transaction_status='success'
        )

        order.status = 'paid'
        order.save()

        Notification.objects.create(
            user=request.user,
            message=f'سفارش شماره {order.id} با موفقیت ثبت شد',
            type='order'
        )

        send_notification_email(
            'تأیید ثبت سفارش',
            f'سفارش شما با شماره {order.id} با موفقیت ثبت شد.',
            request.user.email
        )

        return redirect('order_confirmation', order.id)

    return render(request, 'main/payment.html', {'order': order})


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='paid')
    return render(request, 'main/order_confirmation.html', {'order': order})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['pending', 'paid']:
        order.status = 'canceled'
        order.save()

    return redirect('order_history')


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'main/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'main/order_detail.html', {
        'order': order,
        'items': items
    })



@login_required
def profile_view(request):
    return render(request, 'main/profile.html')


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST or None,
        instance=request.user
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'اطلاعات پروفایل به‌روزرسانی شد.')
        return redirect('edit_profile')

    addresses = Address.objects.filter(user=request.user)

    return render(request, 'main/profile_edit.html', {
        'form': form,
        'addresses': addresses
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('home')
    return render(request, 'main/delete_account.html')



@login_required
def add_review_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        Review.objects.create(
            user=request.user,
            book=book,
            rating=request.POST['rating'],
            comment=request.POST.get('comment', '')
        )
        return redirect('book_detail', book_id)
    return render(request, 'main/add_review.html', {'book': book})



@login_required
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-id')
    return render(request, 'main/notifications.html', {'notifications': notifications})



@login_required
def create_support(request):
    form = SupportForm(request.POST or None)
    if form.is_valid():
        support = form.save(commit=False)
        support.user = request.user
        support.status = 'open'
        support.save()
        return redirect('support_list')
    return render(request, 'main/create_support.html', {'form': form})


@login_required
def support_list(request):
    supports = Support.objects.filter(user=request.user).order_by('-id')
    return render(request, 'main/support_list.html', {'supports': supports})



@login_required
def add_address(request):
    from .forms import AddressForm
    form = AddressForm(request.POST or None)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        return redirect('edit_profile')
    return render(request, 'main/address_form.html', {'form': form})



@login_required
def edit_address(request, address_id):
    from .forms import AddressForm
    address = get_object_or_404(Address, id=address_id, user=request.user)
    form = AddressForm(request.POST or None, instance=address)
    if form.is_valid():
        form.save()
        return redirect('edit_profile')
    return render(request, 'main/address_form.html', {'form': form})



@login_required
def add_address(request):
    form = AddressForm(request.POST or None)

    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user

        if address.is_default:
            Address.objects.filter(
                user=request.user,
                is_default=True
            ).update(is_default=False)

        address.save()
        messages.success(request, 'آدرس با موفقیت اضافه شد.')
        return redirect('profile')

    return render(request, 'main/address_form.html', {
        'form': form,
        'title': 'افزودن آدرس'
    })


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    form = AddressForm(request.POST or None, instance=address)

    if form.is_valid():
        address = form.save(commit=False)

        if address.is_default:
            Address.objects.filter(
                user=request.user,
                is_default=True
            ).exclude(id=address.id).update(is_default=False)

        address.save()
        messages.success(request, 'آدرس ویرایش شد.')
        return redirect('profile')

    return render(request, 'main/address_form.html', {
        'form': form,
        'title': 'ویرایش آدرس'
    })


@login_required
def create_support(request):
    form = SupportForm(request.POST or None)
    if form.is_valid():
        support = form.save(commit=False)
        support.user = request.user
        support.status = 'open'
        support.save()
        return redirect('support_list')
    return render(request, 'main/create_support.html', {'form': form})


@login_required
def support_list(request):
    supports = Support.objects.filter(user=request.user)
    return render(request, 'main/support_list.html', {'supports': supports})



@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect('notifications')
