from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('', views.home_view, name='home'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),

    path('address/add/', views.add_address, name='add_address'),
    path('address/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('address/<int:address_id>/delete/', views.delete_address, name='delete_address'),

    path('books/', views.book_list_view, name='book_list'),
    path('books/<int:book_id>/', views.book_detail_view, name='book_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart_quantity, name='update_cart_quantity'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist_view, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist_view, name='remove_from_wishlist'),


    path('checkout/', views.checkout_view, name='checkout'),

    path('orders/', views.order_history_view, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),


    path('order/<int:order_id>/payment/', views.online_payment, name='online_payment'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),


    path('reviews/add/<int:book_id>/', views.add_review_view, name='add_review'),

    path('notifications/', views.user_notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/',views.mark_notification_read, name='mark_notification_read'),

    path('support/new/', views.create_support, name='create_support'),
    path('support/', views.support_list, name='support_list'),


    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='main/password_reset.html'), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),


    path("chatbot/", views.chatbot_api, name="chatbot_api"),
]


