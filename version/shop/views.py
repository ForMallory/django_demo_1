from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import (
    User, Family, FamilyProfile, Category, Product, 
    Cart, CartItem, Order, OrderItem, UserBehavior
)
from .recommender import get_user_recommendations
from django.db import transaction


def register(request):
    """用户注册"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password', '123456')
        family_name = request.POST.get('family_name')
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'register.html')
        
        # 获取或创建家庭
        family, created = Family.objects.get_or_create(name=family_name)
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            family=family
        )
        
        # 如果是新家庭，创建家庭画像和购物车
        if created:
            FamilyProfile.objects.create(family=family)
            Cart.objects.create(family=family)
        
        messages.success(request, '注册成功！请登录')
        return redirect('login')
    
    return render(request, 'register.html')


def user_login(request):
    """用户登录"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'login.html')


def user_logout(request):
    """用户登出"""
    logout(request)
    return redirect('login')


@login_required
def home(request):
    """首页"""
    user = request.user
    
    # 获取家庭画像
    family_profile = None
    if user.family:
        family_profile, _ = FamilyProfile.objects.get_or_create(family=user.family)
    
    # 获取推荐列表
    recommendations = get_user_recommendations(user, top_n=10)
    
    # 获取购物车信息
    cart = None
    cart_count = 0
    if user.family:
        cart, _ = Cart.objects.get_or_create(family=user.family)
        cart_count = cart.get_items_count()
    
    # 获取热门商品
    popular_products = Product.objects.annotate(
        behavior_count=Count('behaviors')
    ).order_by('-behavior_count')[:8]
    
    context = {
        'user': user,
        'family_profile': family_profile,
        'recommendations': recommendations,
        'popular_products': popular_products,
        'cart_count': cart_count,
    }
    
    return render(request, 'home.html', context)


@login_required
def products(request):
    """商品浏览页面"""
    # 获取所有分类
    categories = Category.objects.all()
    
    # 获取筛选参数
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')
    
    # 构建查询
    products_list = Product.objects.all()
    
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    products_list = products_list.order_by('-created_at')
    
    # 获取购物车数量
    cart_count = 0
    if request.user.family:
        cart = Cart.objects.filter(family=request.user.family).first()
        if cart:
            cart_count = cart.get_items_count()
    
    context = {
        'products': products_list,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'cart_count': cart_count,
    }
    
    return render(request, 'products.html', context)


@login_required
def product_detail(request, product_id):
    """商品详情"""
    product = get_object_or_404(Product, id=product_id)
    
    # 记录浏览行为
    UserBehavior.objects.create(
        user=request.user,
        product=product,
        behavior_type='view'
    )
    
    # 获取相似商品（同分类）
    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    # 获取购物车数量
    cart_count = 0
    if request.user.family:
        cart = Cart.objects.filter(family=request.user.family).first()
        if cart:
            cart_count = cart.get_items_count()
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'cart_count': cart_count,
    }
    
    return render(request, 'product_detail.html', context)


@login_required
def cart_view(request):
    """购物车页面"""
    if not request.user.family:
        messages.error(request, '您还没有加入家庭')
        return redirect('home')
    
    cart, _ = Cart.objects.get_or_create(family=request.user.family)
    cart_items = cart.items.all().select_related('product')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_count': cart.get_items_count(),
    }
    
    return render(request, 'cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """添加商品到购物车"""
    if not request.user.family:
        messages.error(request, '您还没有加入家庭')
        return redirect('products')
    
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(family=request.user.family)
    
    # 检查库存
    if product.stock <= 0:
        messages.error(request, '商品库存不足')
        return redirect('products')
    
    # 添加或更新购物车项
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # 记录行为
    UserBehavior.objects.create(
        user=request.user,
        product=product,
        behavior_type='add_to_cart'
    )
    
    messages.success(request, f'{product.name} 已添加到购物车')
    return redirect(request.META.get('HTTP_REFERER', 'products'))


@login_required
def update_cart_item(request, item_id):
    """更新购物车项数量"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # 检查权限
        if cart_item.cart.family != request.user.family:
            return JsonResponse({'success': False, 'error': '无权限'})
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            # 检查库存
            if quantity > cart_item.product.stock:
                return JsonResponse({'success': False, 'error': '库存不足'})
            
            cart_item.quantity = quantity
            cart_item.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def remove_from_cart(request, item_id):
    """从购物车移除商品"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # 检查权限
    if cart_item.cart.family != request.user.family:
        messages.error(request, '无权限操作')
        return redirect('cart')
    
    cart_item.delete()
    messages.success(request, '商品已从购物车移除')
    return redirect('cart')


@login_required
@transaction.atomic
def checkout(request):
    """结算"""
    if not request.user.family:
        messages.error(request, '您还没有加入家庭')
        return redirect('home')
    
    cart = get_object_or_404(Cart, family=request.user.family)
    cart_items = cart.items.all().select_related('product')
    
    if not cart_items:
        messages.error(request, '购物车为空')
        return redirect('cart')
    
    # 检查库存
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'{item.product.name} 库存不足')
            return redirect('cart')
    
    # 创建订单
    total_price = cart.get_total_price()
    order = Order.objects.create(
        family=request.user.family,
        user=request.user,
        total_price=total_price,
        status='paid'
    )
    
    # 创建订单项并更新库存
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        
        # 更新库存
        item.product.stock -= item.quantity
        item.product.save()
        
        # 记录购买行为
        UserBehavior.objects.create(
            user=request.user,
            product=item.product,
            behavior_type='purchase'
        )
    
    # 清空购物车
    cart_items.delete()
    
    messages.success(request, f'订单创建成功！订单号：{order.id}')
    return redirect('order_detail', order_id=order.id)


@login_required
def profile(request):
    """个人中心"""
    user = request.user
    
    # 获取用户订单
    orders = Order.objects.filter(family=user.family).order_by('-created_at')[:10]
    
    # 获取家庭画像
    family_profile = None
    if user.family:
        family_profile, _ = FamilyProfile.objects.get_or_create(family=user.family)
    
    # 获取所有分类
    categories = Category.objects.all()
    
    # 获取购物车数量
    cart_count = 0
    if user.family:
        cart = Cart.objects.filter(family=user.family).first()
        if cart:
            cart_count = cart.get_items_count()
    
    context = {
        'user': user,
        'orders': orders,
        'family_profile': family_profile,
        'categories': categories,
        'cart_count': cart_count,
    }
    
    return render(request, 'profile.html', context)


@login_required
def update_family_profile(request):
    """更新家庭画像"""
    if request.method == 'POST':
        if not request.user.family:
            messages.error(request, '您还没有加入家庭')
            return redirect('profile')
        
        family_profile, _ = FamilyProfile.objects.get_or_create(family=request.user.family)
        
        # 获取选中的分类
        category_ids = request.POST.getlist('categories')
        family_profile.preferred_categories.set(category_ids)
        
        messages.success(request, '家庭画像更新成功')
        return redirect('profile')
    
    return redirect('profile')


@login_required
def order_detail(request, order_id):
    """订单详情"""
    order = get_object_or_404(Order, id=order_id)
    
    # 检查权限
    if order.family != request.user.family:
        messages.error(request, '无权限查看此订单')
        return redirect('profile')
    
    order_items = order.items.all().select_related('product')
    
    # 获取购物车数量
    cart_count = 0
    if request.user.family:
        cart = Cart.objects.filter(family=request.user.family).first()
        if cart:
            cart_count = cart.get_items_count()
    
    context = {
        'order': order,
        'order_items': order_items,
        'cart_count': cart_count,
    }
    
    return render(request, 'order_detail.html', context)
