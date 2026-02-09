from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class Family(models.Model):
    """家庭模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='家庭名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '家庭'
        verbose_name_plural = '家庭'
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """用户模型 - 扩展Django默认用户"""
    family = models.ForeignKey(
        Family, 
        on_delete=models.CASCADE, 
        related_name='members',
        null=True,
        blank=True,
        verbose_name='所属家庭'
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username


class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=100, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
    
    def __str__(self):
        return self.name


class FamilyProfile(models.Model):
    """家庭画像 - 存储家庭偏好的商品分类"""
    family = models.OneToOneField(
        Family, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name='家庭'
    )
    preferred_categories = models.ManyToManyField(
        Category, 
        related_name='families',
        verbose_name='偏好分类'
    )
    
    class Meta:
        verbose_name = '家庭画像'
        verbose_name_plural = '家庭画像'
    
    def __str__(self):
        return f'{self.family.name}的画像'


class Product(models.Model):
    """商品模型"""
    name = models.CharField(max_length=200, verbose_name='商品名称')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name='商品分类'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    stock = models.IntegerField(default=0, verbose_name='库存')
    lifecycle = models.IntegerField(
        default=30, 
        verbose_name='生命周期(天)',
        help_text='商品使用完的预计天数'
    )
    description = models.TextField(blank=True, verbose_name='商品描述')
    image = models.CharField(max_length=500, blank=True, verbose_name='商品图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
    
    def __str__(self):
        return self.name


class Cart(models.Model):
    """购物车 - 每个家庭一个购物车"""
    family = models.OneToOneField(
        Family, 
        on_delete=models.CASCADE, 
        related_name='cart',
        verbose_name='家庭'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
    
    def __str__(self):
        return f'{self.family.name}的购物车'
    
    def get_total_price(self):
        """计算购物车总价"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_items_count(self):
        """获取购物车商品数量"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """购物车项"""
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name='购物车'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name='商品'
    )
    quantity = models.IntegerField(default=1, verbose_name='数量')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    
    class Meta:
        verbose_name = '购物车项'
        verbose_name_plural = '购物车项'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    def get_total_price(self):
        """计算该项总价"""
        return self.product.price * self.quantity


class Order(models.Model):
    """订单"""
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    family = models.ForeignKey(
        Family, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name='家庭'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='orders',
        verbose_name='下单用户'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='订单状态'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'订单 #{self.id} - {self.family.name}'


class OrderItem(models.Model):
    """订单项"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name='订单'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name='商品'
    )
    quantity = models.IntegerField(verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name='购买时间')
    
    class Meta:
        verbose_name = '订单项'
        verbose_name_plural = '订单项'
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    def get_total_price(self):
        """计算该项总价"""
        return self.price * self.quantity
    
    def should_recommend(self):
        """判断是否应该推荐（生命周期剩余30%）"""
        if not self.product.lifecycle:
            return False
        days_passed = (timezone.now() - self.purchase_date).days
        lifecycle_percentage = days_passed / self.product.lifecycle
        return lifecycle_percentage >= 0.7


class UserBehavior(models.Model):
    """用户行为记录"""
    BEHAVIOR_CHOICES = [
        ('view', '浏览'),
        ('add_to_cart', '加入购物车'),
        ('purchase', '购买'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='behaviors',
        verbose_name='用户'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='behaviors',
        verbose_name='商品'
    )
    behavior_type = models.CharField(
        max_length=20, 
        choices=BEHAVIOR_CHOICES,
        verbose_name='行为类型'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='时间戳')
    
    # 用于协同过滤的评分（浏览=1, 加入购物车=3, 购买=5）
    BEHAVIOR_SCORES = {
        'view': 1,
        'add_to_cart': 3,
        'purchase': 5,
    }
    
    class Meta:
        verbose_name = '用户行为'
        verbose_name_plural = '用户行为'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_behavior_type_display()} - {self.product.name}'
    
    def get_score(self):
        """获取行为评分"""
        return self.BEHAVIOR_SCORES.get(self.behavior_type, 0)
