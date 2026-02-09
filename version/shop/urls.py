from django.urls import path
from . import views

urlpatterns = [
    # 认证
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 主页
    path('', views.home, name='home'),
    
    # 商品
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # 购物车
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # 个人中心
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_family_profile, name='update_family_profile'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]

