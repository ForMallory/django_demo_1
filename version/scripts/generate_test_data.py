"""
测试数据生成脚本
生成40个用户、20个家庭、15个分类、400个商品和用户行为数据
"""
import os
import sys
import django
import random
from datetime import timedelta
from django.utils import timezone

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'version.settings')
django.setup()

from shop.models import (
    User, Family, FamilyProfile, Category, Product,
    Cart, Order, OrderItem, UserBehavior
)

# 商品分类列表
CATEGORIES = [
    '食品饮料', '生鲜果蔬', '美妆护肤', '个人护理', '家居清洁',
    '厨房用品', '家居装饰', '床上用品', '母婴用品', '宠物用品',
    '数码配件', '运动健身', '图书文具', '服装鞋帽', '箱包配饰'
]

# 商品名称模板
PRODUCT_TEMPLATES = {
    '食品饮料': ['牛奶', '酸奶', '果汁', '咖啡', '茶叶', '饼干', '薯片', '巧克力', '糖果', '方便面'],
    '生鲜果蔬': ['苹果', '香蕉', '橙子', '葡萄', '西瓜', '白菜', '萝卜', '土豆', '西红柿', '黄瓜'],
    '美妆护肤': ['面膜', '洗面奶', '爽肤水', '乳液', '精华液', '口红', '眼影', '粉底液', '防晒霜', '卸妆水'],
    '个人护理': ['牙膏', '牙刷', '洗发水', '护发素', '沐浴露', '香皂', '毛巾', '剃须刀', '梳子', '指甲钳'],
    '家居清洁': ['洗衣液', '洗洁精', '消毒液', '拖把', '扫把', '垃圾袋', '抹布', '清洁剂', '除菌液', '空气清新剂'],
    '厨房用品': ['锅具', '碗碟', '筷子', '勺子', '刀具', '砧板', '保鲜盒', '保鲜膜', '厨房纸', '围裙'],
    '家居装饰': ['相框', '花瓶', '装饰画', '抱枕', '地毯', '窗帘', '台灯', '挂钟', '摆件', '绿植'],
    '床上用品': ['床单', '被套', '枕头', '被子', '毛毯', '床垫', '枕套', '床笠', '凉席', '蚊帐'],
    '母婴用品': ['奶粉', '纸尿裤', '奶瓶', '婴儿车', '玩具', '婴儿服', '湿巾', '爬行垫', '安抚奶嘴', '儿童餐具'],
    '宠物用品': ['猫粮', '狗粮', '宠物玩具', '猫砂', '宠物窝', '牵引绳', '宠物碗', '宠物零食', '宠物梳子', '宠物衣服'],
    '数码配件': ['数据线', '充电器', '耳机', '手机壳', '屏幕保护膜', '移动电源', '鼠标', '键盘', 'U盘', '读卡器'],
    '运动健身': ['瑜伽垫', '哑铃', '跳绳', '运动服', '运动鞋', '护腕', '运动水杯', '健身手套', '弹力带', '瑜伽球'],
    '图书文具': ['笔记本', '钢笔', '铅笔', '橡皮', '尺子', '书签', '便签', '文件夹', '订书机', '胶带'],
    '服装鞋帽': ['T恤', '衬衫', '裤子', '裙子', '外套', '运动鞋', '拖鞋', '帽子', '围巾', '手套'],
    '箱包配饰': ['背包', '手提包', '钱包', '腰带', '手表', '太阳镜', '项链', '耳环', '手链', '戒指']
}

def generate_data():
    print("开始生成测试数据...")
    
    # 清空现有数据（除了超级管理员）
    print("清空现有数据...")
    UserBehavior.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Cart.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    FamilyProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    Family.objects.all().delete()
    
    # 1. 创建15个商品分类
    print("创建商品分类...")
    categories = []
    for cat_name in CATEGORIES:
        category = Category.objects.create(
            name=cat_name,
            description=f'{cat_name}相关商品'
        )
        categories.append(category)
    print(f"✓ 创建了 {len(categories)} 个商品分类")
    
    # 2. 创建20个家庭
    print("创建家庭...")
    families = []
    for i in range(1, 21):
        family = Family.objects.create(name=f'家庭{i}')
        families.append(family)
        
        # 为每个家庭创建画像，随机选择5-8个偏好分类
        profile = FamilyProfile.objects.create(family=family)
        preferred_cats = random.sample(categories, random.randint(5, 8))
        profile.preferred_categories.set(preferred_cats)
        
        # 为每个家庭创建购物车
        Cart.objects.create(family=family)
    print(f"✓ 创建了 {len(families)} 个家庭")
    
    # 3. 创建40个用户（每个家庭2个用户）
    print("创建用户...")
    users = []
    for i, family in enumerate(families):
        for j in range(2):
            username = f'user{i*2+j+1}'
            user = User.objects.create_user(
                username=username,
                password='123456',
                family=family
            )
            users.append(user)
    print(f"✓ 创建了 {len(users)} 个用户")
    
    # 4. 创建400个商品
    print("创建商品...")
    products = []
    products_per_category = 400 // len(categories)
    extra_products = 400 % len(categories)
    
    for idx, category in enumerate(categories):
        num_products = products_per_category + (1 if idx < extra_products else 0)
        templates = PRODUCT_TEMPLATES.get(category.name, ['商品'])
        
        for i in range(num_products):
            template = templates[i % len(templates)]
            product = Product.objects.create(
                name=f'{template}{i+1}',
                category=category,
                price=round(random.uniform(10, 500), 2),
                stock=random.randint(50, 500),
                lifecycle=random.choice([7, 15, 30, 60, 90, 180]),
                description=f'这是一款优质的{category.name}商品'
            )
            products.append(product)
    print(f"✓ 创建了 {len(products)} 个商品")
    
    # 5. 生成用户行为数据
    print("生成用户行为数据...")
    total_behaviors = 0
    total_purchases = 0
    
    for user in users:
        # 每个用户至少5个行为
        num_behaviors = random.randint(5, 15)
        
        # 随机选择商品
        user_products = random.sample(products, min(num_behaviors, len(products)))
        
        # 确保至少2个购买行为
        purchase_count = 0
        
        for product in user_products:
            # 浏览行为
            UserBehavior.objects.create(
                user=user,
                product=product,
                behavior_type='view'
            )
            total_behaviors += 1
            
            # 50%概率加入购物车
            if random.random() < 0.5:
                UserBehavior.objects.create(
                    user=user,
                    product=product,
                    behavior_type='add_to_cart'
                )
                total_behaviors += 1
                
                # 30%概率购买
                if random.random() < 0.3 or purchase_count < 2:
                    UserBehavior.objects.create(
                        user=user,
                        product=product,
                        behavior_type='purchase'
                    )
                    total_behaviors += 1
                    purchase_count += 1
        
        # 确保至少2个购买行为
        while purchase_count < 2:
            product = random.choice(products)
            UserBehavior.objects.create(
                user=user,
                product=product,
                behavior_type='purchase'
            )
            total_behaviors += 1
            purchase_count += 1
        
        total_purchases += purchase_count
    
    print(f"✓ 生成了 {total_behaviors} 个用户行为记录")
    print(f"✓ 其中购买行为 {total_purchases} 个")
    
    # 6. 根据购买行为创建订单
    print("创建订单...")
    purchase_behaviors = UserBehavior.objects.filter(behavior_type='purchase')
    
    # 按用户和时间分组创建订单
    orders_created = 0
    for user in users:
        user_purchases = purchase_behaviors.filter(user=user)
        
        if user_purchases.exists():
            # 每2-3个购买行为创建一个订单
            purchase_list = list(user_purchases)
            random.shuffle(purchase_list)
            
            i = 0
            while i < len(purchase_list):
                batch_size = random.randint(1, 3)
                batch = purchase_list[i:i+batch_size]
                
                # 计算订单总价
                total_price = sum(b.product.price for b in batch)
                
                # 创建订单
                order = Order.objects.create(
                    family=user.family,
                    user=user,
                    total_price=total_price,
                    status='paid'
                )
                
                # 创建订单项
                for behavior in batch:
                    OrderItem.objects.create(
                        order=order,
                        product=behavior.product,
                        quantity=random.randint(1, 3),
                        price=behavior.product.price
                    )
                
                orders_created += 1
                i += batch_size
    
    print(f"✓ 创建了 {orders_created} 个订单")
    
    # 7. 创建超级管理员
    print("创建超级管理员...")
    if not User.objects.filter(username='mallory').exists():
        User.objects.create_superuser(
            username='mallory',
            password='123456',
            email='mallory@example.com'
        )
        print("✓ 创建超级管理员 mallory")
    else:
        print("✓ 超级管理员 mallory 已存在")
    
    print("\n" + "="*50)
    print("数据生成完成！")
    print("="*50)
    print(f"商品分类: {Category.objects.count()} 个")
    print(f"家庭: {Family.objects.count()} 个")
    print(f"用户: {User.objects.filter(is_superuser=False).count()} 个")
    print(f"商品: {Product.objects.count()} 个")
    print(f"用户行为: {UserBehavior.objects.count()} 个")
    print(f"订单: {Order.objects.count()} 个")
    print("="*50)
    print("\n登录信息：")
    print("管理员账号: mallory / 123456")
    print("用户账号: user1-user40 / 123456")
    print("="*50)

if __name__ == '__main__':
    generate_data()

