"""
推荐系统引擎 - 基于协同过滤算法
"""
import numpy as np
from collections import defaultdict
from django.db.models import Count, Q
from .models import UserBehavior, Product, User, OrderItem
from django.utils import timezone


class RecommenderSystem:
    """推荐系统类"""
    
    def __init__(self, alpha=0.5):
        """
        初始化推荐系统
        :param alpha: 用户协同过滤和商品协同过滤的权重 (0-1之间)
        """
        self.alpha = alpha
        self.user_item_matrix = None
        self.item_user_matrix = None
        self.users = []
        self.products = []
        
    def build_matrices(self):
        """构建用户-商品评分矩阵"""
        # 获取所有用户和商品
        self.users = list(User.objects.filter(is_superuser=False).values_list('id', flat=True))
        self.products = list(Product.objects.values_list('id', flat=True))
        
        if not self.users or not self.products:
            return
        
        # 创建用户和商品的索引映射
        user_idx = {user_id: idx for idx, user_id in enumerate(self.users)}
        product_idx = {product_id: idx for idx, product_id in enumerate(self.products)}
        
        # 初始化矩阵
        n_users = len(self.users)
        n_products = len(self.products)
        self.user_item_matrix = np.zeros((n_users, n_products))
        
        # 填充评分矩阵
        behaviors = UserBehavior.objects.all()
        for behavior in behaviors:
            if behavior.user_id in user_idx and behavior.product_id in product_idx:
                u_idx = user_idx[behavior.user_id]
                p_idx = product_idx[behavior.product_id]
                self.user_item_matrix[u_idx, p_idx] += behavior.get_score()
        
        # 转置得到商品-用户矩阵
        self.item_user_matrix = self.user_item_matrix.T
        
        return user_idx, product_idx
    
    def cosine_similarity(self, matrix):
        """
        计算余弦相似度
        :param matrix: 输入矩阵
        :return: 相似度矩阵
        """
        # 计算每行的范数
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # 避免除零
        
        # 归一化
        normalized_matrix = matrix / norms
        
        # 计算余弦相似度
        similarity = np.dot(normalized_matrix, normalized_matrix.T)
        
        return similarity
    
    def normalize_scores(self, scores):
        """
        归一化评分到0-1之间
        :param scores: 原始评分
        :return: 归一化后的评分
        """
        if len(scores) == 0:
            return scores
        
        min_score = np.min(scores)
        max_score = np.max(scores)
        
        if max_score == min_score:
            return np.ones_like(scores) * 0.5
        
        return (scores - min_score) / (max_score - min_score)
    
    def user_based_cf(self, user_id, user_idx, product_idx, top_n=10):
        """
        基于用户的协同过滤
        :param user_id: 目标用户ID
        :param user_idx: 用户索引映射
        :param product_idx: 商品索引映射
        :param top_n: 返回top N个推荐
        :return: 推荐商品ID列表及评分
        """
        if user_id not in user_idx:
            return []
        
        u_idx = user_idx[user_id]
        
        # 计算用户相似度
        user_similarity = self.cosine_similarity(self.user_item_matrix)
        
        # 获取目标用户的相似用户（排除自己）
        similarities = user_similarity[u_idx].copy()
        similarities[u_idx] = 0  # 排除自己
        
        # 预测评分
        predictions = np.dot(similarities, self.user_item_matrix)
        
        # 排除用户已经交互过的商品
        user_interacted = self.user_item_matrix[u_idx] > 0
        predictions[user_interacted] = -1
        
        return predictions
    
    def item_based_cf(self, user_id, user_idx, product_idx, top_n=10):
        """
        基于商品的协同过滤
        :param user_id: 目标用户ID
        :param user_idx: 用户索引映射
        :param product_idx: 商品索引映射
        :param top_n: 返回top N个推荐
        :return: 推荐商品ID列表及评分
        """
        if user_id not in user_idx:
            return []
        
        u_idx = user_idx[user_id]
        
        # 计算商品相似度
        item_similarity = self.cosine_similarity(self.item_user_matrix)
        
        # 获取用户评分
        user_ratings = self.user_item_matrix[u_idx]
        
        # 预测评分
        predictions = np.dot(user_ratings, item_similarity)
        
        # 排除用户已经交互过的商品
        user_interacted = self.user_item_matrix[u_idx] > 0
        predictions[user_interacted] = -1
        
        return predictions
    
    def get_lifecycle_recommendations(self, user):
        """
        获取基于生命周期的推荐
        :param user: 用户对象
        :return: 需要补充的商品ID列表
        """
        if not user.family:
            return []
        
        # 获取家庭的所有订单项
        order_items = OrderItem.objects.filter(
            order__family=user.family,
            order__status__in=['paid', 'shipped', 'completed']
        ).select_related('product')
        
        lifecycle_products = []
        for item in order_items:
            if item.should_recommend():
                lifecycle_products.append(item.product.id)
        
        return lifecycle_products
    
    def get_recommendations(self, user, top_n=10):
        """
        获取综合推荐结果
        :param user: 用户对象
        :param top_n: 返回top N个推荐
        :return: 推荐商品列表
        """
        # 构建矩阵
        result = self.build_matrices()
        if result is None:
            return []
        
        user_idx, product_idx = result
        
        # 获取生命周期推荐
        lifecycle_products = self.get_lifecycle_recommendations(user)
        
        # 如果用户不在索引中，返回热门商品
        if user.id not in user_idx:
            popular_products = Product.objects.annotate(
                behavior_count=Count('behaviors')
            ).order_by('-behavior_count')[:top_n]
            return list(popular_products)
        
        # 基于用户的协同过滤
        user_based_scores = self.user_based_cf(user.id, user_idx, product_idx, top_n)
        
        # 基于商品的协同过滤
        item_based_scores = self.item_based_cf(user.id, user_idx, product_idx, top_n)
        
        # 加权融合
        if len(user_based_scores) > 0 and len(item_based_scores) > 0:
            # 归一化
            user_based_scores = self.normalize_scores(user_based_scores)
            item_based_scores = self.normalize_scores(item_based_scores)
            
            # 加权
            final_scores = self.alpha * user_based_scores + (1 - self.alpha) * item_based_scores
        else:
            final_scores = user_based_scores if len(user_based_scores) > 0 else item_based_scores
        
        # 提升生命周期商品的评分
        product_idx_reverse = {idx: product_id for product_id, idx in product_idx.items()}
        for idx, product_id in product_idx_reverse.items():
            if product_id in lifecycle_products:
                final_scores[idx] += 2.0  # 大幅提升生命周期商品的评分
        
        # 获取top N推荐
        top_indices = np.argsort(final_scores)[::-1][:top_n]
        
        # 转换为商品ID
        product_idx_reverse = {idx: product_id for product_id, idx in product_idx.items()}
        recommended_product_ids = [product_idx_reverse[idx] for idx in top_indices if final_scores[idx] > 0]
        
        # 获取商品对象
        recommended_products = Product.objects.filter(id__in=recommended_product_ids)
        
        # 按推荐顺序排序
        product_dict = {p.id: p for p in recommended_products}
        ordered_products = [product_dict[pid] for pid in recommended_product_ids if pid in product_dict]
        
        return ordered_products


def get_user_recommendations(user, top_n=10):
    """
    便捷函数：获取用户推荐
    :param user: 用户对象
    :param top_n: 返回top N个推荐
    :return: 推荐商品列表
    """
    recommender = RecommenderSystem(alpha=0.5)
    return recommender.get_recommendations(user, top_n)

