from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import signup_view, CustomLoginView, CustomLogoutView

urlpatterns = [
    path('', views.home_view, name='home'),
    path('books/', views.book_list_view, name='book_list'),
    path('books/<int:book_id>/', views.book_detail_view, name='book_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist_view, name='add_to_wishlist'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.orders_view, name='orders'),

    path('login/', CustomLoginView.as_view(), name='login'),

    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('signup/', signup_view, name='signup'),
]

