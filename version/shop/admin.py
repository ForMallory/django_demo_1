from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Family, FamilyProfile, Category, Product,
    Cart, CartItem, Order, OrderItem, UserBehavior
)

# 自定义Admin站点标题
admin.site.site_header = '家用商品推荐系统 - 管理后台'
admin.site.site_title = '管理后台'
admin.site.index_title = '欢迎使用家用商品推荐系统管理后台'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'family', 'is_staff', 'is_superuser', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'family', 'date_joined']
    search_fields = ['username', 'email', 'family__name']
    ordering = ['-date_joined']
    list_per_page = 20
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('家庭信息', {'fields': ('family',)}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('family')


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'member_count', 'has_profile', 'has_cart']
    search_fields = ['name']
    ordering = ['-created_at']
    list_per_page = 20
    readonly_fields = ['created_at']
    
    def member_count(self, obj):
        count = obj.members.count()
        return format_html('<span style="color: #667eea; font-weight: bold;">{}</span>', count)
    member_count.short_description = '成员数量'
    
    def has_profile(self, obj):
        has = hasattr(obj, 'profile')
        color = 'green' if has else 'red'
        text = '✓' if has else '✗'
        return format_html('<span style="color: {}; font-size: 16px;">{}</span>', color, text)
    has_profile.short_description = '有画像'
    
    def has_cart(self, obj):
        has = hasattr(obj, 'cart')
        color = 'green' if has else 'red'
        text = '✓' if has else '✗'
        return format_html('<span style="color: {}; font-size: 16px;">{}</span>', color, text)
    has_cart.short_description = '有购物车'


@admin.register(FamilyProfile)
class FamilyProfileAdmin(admin.ModelAdmin):
    list_display = ['family', 'get_categories', 'category_count']
    filter_horizontal = ['preferred_categories']
    search_fields = ['family__name']
    list_per_page = 20
    
    def get_categories(self, obj):
        categories = obj.preferred_categories.all()[:5]
        if categories:
            return ', '.join([c.name for c in categories]) + ('...' if obj.preferred_categories.count() > 5 else '')
        return '未设置'
    get_categories.short_description = '偏好分类'
    
    def category_count(self, obj):
        count = obj.preferred_categories.count()
        return format_html('<span style="color: #667eea; font-weight: bold;">{}</span>', count)
    category_count.short_description = '分类数量'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'product_count']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_per_page = 20
    
    def product_count(self, obj):
        count = obj.products.count()
        return format_html('<span style="color: #667eea; font-weight: bold;">{}</span>', count)
    product_count.short_description = '商品数量'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_display', 'stock', 'lifecycle', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['stock']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'description')
        }),
        ('价格和库存', {
            'fields': ('price', 'stock')
        }),
        ('生命周期', {
            'fields': ('lifecycle',),
            'description': '商品使用完的预计天数，剩余30%时会自动推荐'
        }),
        ('其他信息', {
            'fields': ('image', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        return format_html('<span style="color: #667eea; font-weight: bold;">¥{}</span>', obj.price)
    price_display.short_description = '价格'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'added_at', 'get_total_price']
    can_delete = True
    
    def get_total_price(self, obj):
        return f'¥{obj.get_total_price()}'
    get_total_price.short_description = '小计'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['family', 'get_items_count', 'get_total_price', 'updated_at']
    search_fields = ['family__name']
    ordering = ['-updated_at']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_items_count(self, obj):
        count = obj.get_items_count()
        return format_html('<span style="color: #667eea; font-weight: bold;">{}</span>', count)
    get_items_count.short_description = '商品数量'
    
    def get_total_price(self, obj):
        price = obj.get_total_price()
        return format_html('<span style="color: #667eea; font-weight: bold;">¥{}</span>', price)
    get_total_price.short_description = '总价'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'purchase_date', 'get_total_price']
    can_delete = False
    
    def get_total_price(self, obj):
        return f'¥{obj.get_total_price()}'
    get_total_price.short_description = '小计'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'family', 'user', 'status_display', 'total_price_display', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['family__name', 'user__username', 'id']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('订单信息', {
            'fields': ('family', 'user', 'status')
        }),
        ('价格信息', {
            'fields': ('total_price',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        status_colors = {
            'pending': '#ffa500',
            'paid': '#28a745',
            'shipped': '#17a2b8',
            'completed': '#667eea',
            'cancelled': '#dc3545',
        }
        color = status_colors.get(obj.status, '#666')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = '订单状态'
    
    def total_price_display(self, obj):
        return format_html('<span style="color: #667eea; font-weight: bold;">¥{}</span>', obj.total_price)
    total_price_display.short_description = '总价'


@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'behavior_type_display', 'get_score_display', 'timestamp']
    list_filter = ['behavior_type', 'timestamp']
    search_fields = ['user__username', 'product__name']
    ordering = ['-timestamp']
    list_per_page = 100
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('行为信息', {
            'fields': ('user', 'product', 'behavior_type')
        }),
        ('时间信息', {
            'fields': ('timestamp',)
        }),
    )
    
    def behavior_type_display(self, obj):
        behavior_colors = {
            'view': '#17a2b8',
            'add_to_cart': '#ffc107',
            'purchase': '#28a745',
        }
        color = behavior_colors.get(obj.behavior_type, '#666')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">{}</span>',
            color, obj.get_behavior_type_display()
        )
    behavior_type_display.short_description = '行为类型'
    
    def get_score_display(self, obj):
        score = obj.get_score()
        return format_html('<span style="color: #667eea; font-weight: bold; font-size: 16px;">{}</span>', score)
    get_score_display.short_description = '评分'


# 自定义CartItem的Admin（如果需要单独管理）
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'added_at', 'get_total_price']
    list_filter = ['added_at']
    search_fields = ['cart__family__name', 'product__name']
    ordering = ['-added_at']
    list_per_page = 50
    readonly_fields = ['added_at']
    
    def get_total_price(self, obj):
        return format_html('<span style="color: #667eea; font-weight: bold;">¥{}</span>', obj.get_total_price())
    get_total_price.short_description = '小计'


# 自定义OrderItem的Admin（如果需要单独管理）
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'purchase_date', 'get_total_price']
    list_filter = ['purchase_date']
    search_fields = ['order__id', 'product__name']
    ordering = ['-purchase_date']
    list_per_page = 50
    readonly_fields = ['purchase_date']
    
    def get_total_price(self, obj):
        return format_html('<span style="color: #667eea; font-weight: bold;">¥{}</span>', obj.get_total_price())
    get_total_price.short_description = '小计'
