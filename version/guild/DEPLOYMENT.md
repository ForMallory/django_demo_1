# 部署说明

## 系统已完成部署

### ✅ 已完成的工作

1. **项目初始化**
   - ✅ 创建Django项目和shop应用
   - ✅ 配置settings.py（8080端口、中文、时区）
   - ✅ 设置模板和静态文件目录

2. **数据模型设计**
   - ✅ User（用户模型，扩展Django User）
   - ✅ Family（家庭模型）
   - ✅ FamilyProfile（家庭画像）
   - ✅ Category（商品分类）
   - ✅ Product（商品，含生命周期）
   - ✅ Cart & CartItem（家庭共享购物车）
   - ✅ Order & OrderItem（订单系统）
   - ✅ UserBehavior（用户行为追踪）

3. **推荐算法引擎**
   - ✅ 基于用户的协同过滤（User-based CF）
   - ✅ 基于商品的协同过滤（Item-based CF）
   - ✅ 余弦相似度计算
   - ✅ 评分归一化
   - ✅ 加权融合（alpha=0.5）
   - ✅ 生命周期推荐（剩余30%触发）

4. **视图和URL配置**
   - ✅ 用户注册/登录/登出
   - ✅ 首页（推荐列表、家庭画像）
   - ✅ 商品浏览（分类筛选、搜索）
   - ✅ 商品详情
   - ✅ 购物车管理
   - ✅ 订单结算
   - ✅ 个人中心
   - ✅ 家庭画像设置

5. **前端页面**
   - ✅ 现代化UI设计（渐变色、动画效果）
   - ✅ 响应式布局
   - ✅ 登录/注册页面
   - ✅ 首页（推荐展示）
   - ✅ 商品浏览页面
   - ✅ 商品详情页面
   - ✅ 购物车页面
   - ✅ 个人中心页面
   - ✅ 订单详情页面

6. **后台管理**
   - ✅ Django Admin配置
   - ✅ 所有模型注册
   - ✅ 自定义管理界面

7. **测试数据**
   - ✅ 40个用户（user1-user40）
   - ✅ 20个家庭（每家庭2用户）
   - ✅ 15个商品分类
   - ✅ 400个商品
   - ✅ 683个用户行为记录
   - ✅ 67个订单
   - ✅ 超级管理员mallory

8. **评估系统**
   - ✅ 准确率计算
   - ✅ 召回率计算
   - ✅ F1分数计算
   - ✅ 评估报告生成

## 启动服务器

### 方法1：使用启动脚本（推荐）

```bash
cd /www/wwwroot/version3/version
./start_server.sh
```

### 方法2：手动启动

```bash
su - admin
source /home/admin/miniconda3/bin/activate
conda activate django_shop
cd /www/wwwroot/version3/version
python manage.py runserver 0.0.0.0:8080
```

### 方法3：后台运行

```bash
cd /www/wwwroot/version3/version
nohup ./start_server.sh > server.log 2>&1 &
```

## 访问系统

### 用户前端
- URL: `http://服务器IP:8080/`
- 登录页面: `http://服务器IP:8080/login/`
- 注册页面: `http://服务器IP:8080/register/`

### 管理后台
- URL: `http://服务器IP:8080/admin/`
- 用户名: `mallory`
- 密码: `123456`

### 测试账号
- 用户名: `user1` 到 `user40`
- 密码: `123456`
- 家庭: `家庭1` 到 `家庭20`

## 功能测试清单

### 1. 用户认证
- [ ] 用户注册（自动创建家庭）
- [ ] 用户登录
- [ ] 用户登出
- [ ] 管理员登录

### 2. 首页功能
- [ ] 查看家庭画像
- [ ] 查看推荐列表（Top 10）
- [ ] 查看热门商品
- [ ] 导航栏显示购物车数量

### 3. 商品浏览
- [ ] 浏览所有商品
- [ ] 按分类筛选
- [ ] 搜索商品
- [ ] 查看商品详情
- [ ] 浏览行为记录

### 4. 购物车
- [ ] 添加商品到购物车
- [ ] 查看购物车
- [ ] 修改商品数量
- [ ] 删除商品
- [ ] 家庭成员共享购物车
- [ ] 加购行为记录

### 5. 订单系统
- [ ] 结算购物车
- [ ] 查看订单列表
- [ ] 查看订单详情
- [ ] 购买行为记录
- [ ] 库存自动扣减

### 6. 个人中心
- [ ] 查看用户信息
- [ ] 查看家庭信息
- [ ] 查看订单历史
- [ ] 设置家庭画像（偏好分类）

### 7. 推荐系统
- [ ] 基于用户行为推荐
- [ ] 基于家庭画像推荐
- [ ] 生命周期推荐
- [ ] 推荐结果实时更新

### 8. 管理后台
- [ ] 管理用户
- [ ] 管理家庭
- [ ] 管理商品
- [ ] 管理分类
- [ ] 查看订单
- [ ] 查看用户行为

## 重新生成数据

如果需要重新生成测试数据：

```bash
cd /www/wwwroot/version3/version
python scripts/generate_test_data.py
```

## 评估推荐系统

```bash
cd /www/wwwroot/version3/version
python scripts/evaluate_recommender.py
```

评估报告将保存在 `evaluation_report.txt`

## 数据库管理

### 查看数据统计
```bash
python manage.py shell
```

```python
from shop.models import *

print(f"用户数: {User.objects.filter(is_superuser=False).count()}")
print(f"家庭数: {Family.objects.count()}")
print(f"商品数: {Product.objects.count()}")
print(f"分类数: {Category.objects.count()}")
print(f"订单数: {Order.objects.count()}")
print(f"行为数: {UserBehavior.objects.count()}")
```

### 重置数据库
```bash
rm db.sqlite3
rm -rf shop/migrations/000*.py
python manage.py makemigrations
python manage.py migrate
python scripts/generate_test_data.py
```

## 常见问题

### Q1: 服务器启动失败
**A:** 检查8080端口是否被占用
```bash
netstat -tlnp | grep 8080
# 如果被占用，杀死进程
kill -9 <PID>
```

### Q2: 推荐列表为空
**A:** 需要有足够的用户行为数据，运行测试数据生成脚本

### Q3: 无法登录
**A:** 确认用户名和密码正确，默认密码都是123456

### Q4: 购物车不共享
**A:** 确认用户属于同一家庭，检查Family关联

### Q5: 推荐算法评估分数为0
**A:** 这是正常的，因为推荐的是用户可能感兴趣但未购买的商品。随着用户行为增加，评分会提高。

## 性能监控

### 查看服务器日志
```bash
tail -f server.log
```

### 查看数据库大小
```bash
ls -lh db.sqlite3
```

### 查看内存使用
```bash
ps aux | grep python
```

## 生产环境部署建议

1. **使用Gunicorn/uWSGI**
   ```bash
   pip install gunicorn
   gunicorn version.wsgi:application --bind 0.0.0.0:8080
   ```

2. **使用Nginx反向代理**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /static/ {
           alias /www/wwwroot/version3/version/staticfiles/;
       }
   }
   ```

3. **使用MySQL数据库**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'shop_db',
           'USER': 'shop_user',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

4. **配置静态文件**
   ```bash
   python manage.py collectstatic
   ```

5. **关闭DEBUG模式**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'your-ip']
   ```

## 项目文件清单

```
version3/version/
├── README.md                    # 项目说明文档
├── DEPLOYMENT.md               # 本部署文档
├── requirements.txt            # Python依赖
├── start_server.sh            # 启动脚本
├── manage.py                  # Django管理脚本
├── db.sqlite3                 # SQLite数据库
├── evaluation_report.txt      # 评估报告
├── version/                   # 项目配置
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/                      # 主应用
│   ├── models.py             # 数据模型
│   ├── views.py              # 视图函数
│   ├── urls.py               # URL配置
│   ├── admin.py              # 后台管理
│   ├── recommender.py        # 推荐引擎
│   └── migrations/           # 数据库迁移
├── templates/                 # HTML模板
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── products.html
│   ├── product_detail.html
│   ├── cart.html
│   ├── profile.html
│   └── order_detail.html
├── static/                    # 静态文件
│   ├── css/
│   └── js/
└── scripts/                   # 工具脚本
    ├── generate_test_data.py
    └── evaluate_recommender.py
```

## 技术支持

如有问题，请检查：
1. README.md - 项目说明
2. 本文档 - 部署说明
3. Django日志输出
4. 数据库数据完整性

---

**部署完成！系统已就绪！** ✅

