"""
推荐系统评估脚本
计算准确率(Precision)、召回率(Recall)和F1分数
"""
import os
import sys
import django
from collections import defaultdict

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'version.settings')
django.setup()

from shop.models import User, UserBehavior, Product
from shop.recommender import RecommenderSystem


def evaluate_recommender():
    """评估推荐系统性能"""
    print("="*60)
    print("推荐系统评估")
    print("="*60)
    
    # 获取所有普通用户
    users = User.objects.filter(is_superuser=False)
    
    if not users.exists():
        print("错误：没有找到用户数据")
        return
    
    # 初始化推荐系统
    recommender = RecommenderSystem(alpha=0.5)
    
    # 存储评估指标
    precision_scores = []
    recall_scores = []
    f1_scores = []
    
    print(f"\n开始评估 {users.count()} 个用户的推荐结果...\n")
    
    for user in users:
        # 获取用户实际购买的商品
        actual_purchases = set(
            UserBehavior.objects.filter(
                user=user,
                behavior_type='purchase'
            ).values_list('product_id', flat=True)
        )
        
        if not actual_purchases:
            continue
        
        # 获取推荐结果
        recommendations = recommender.get_recommendations(user, top_n=10)
        recommended_ids = set([p.id for p in recommendations])
        
        # 计算指标
        if recommended_ids:
            # 真正例（推荐且购买）
            true_positives = len(recommended_ids & actual_purchases)
            
            # 准确率 = 推荐中实际购买的比例
            precision = true_positives / len(recommended_ids) if recommended_ids else 0
            
            # 召回率 = 实际购买中被推荐的比例
            recall = true_positives / len(actual_purchases) if actual_purchases else 0
            
            # F1分数
            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
            else:
                f1 = 0
            
            precision_scores.append(precision)
            recall_scores.append(recall)
            f1_scores.append(f1)
    
    # 计算平均值
    if precision_scores:
        avg_precision = sum(precision_scores) / len(precision_scores)
        avg_recall = sum(recall_scores) / len(recall_scores)
        avg_f1 = sum(f1_scores) / len(f1_scores)
        
        print("="*60)
        print("评估结果")
        print("="*60)
        print(f"评估用户数: {len(precision_scores)}")
        print(f"平均准确率 (Precision): {avg_precision:.4f} ({avg_precision*100:.2f}%)")
        print(f"平均召回率 (Recall):    {avg_recall:.4f} ({avg_recall*100:.2f}%)")
        print(f"平均F1分数 (F1-Score):  {avg_f1:.4f} ({avg_f1*100:.2f}%)")
        print("="*60)
        
        # 详细统计
        print("\n详细统计:")
        print(f"准确率分布:")
        print(f"  最小值: {min(precision_scores):.4f}")
        print(f"  最大值: {max(precision_scores):.4f}")
        print(f"  中位数: {sorted(precision_scores)[len(precision_scores)//2]:.4f}")
        
        print(f"\n召回率分布:")
        print(f"  最小值: {min(recall_scores):.4f}")
        print(f"  最大值: {max(recall_scores):.4f}")
        print(f"  中位数: {sorted(recall_scores)[len(recall_scores)//2]:.4f}")
        
        print(f"\nF1分数分布:")
        print(f"  最小值: {min(f1_scores):.4f}")
        print(f"  最大值: {max(f1_scores):.4f}")
        print(f"  中位数: {sorted(f1_scores)[len(f1_scores)//2]:.4f}")
        
        # 性能等级评估
        print("\n" + "="*60)
        print("性能评估")
        print("="*60)
        
        if avg_f1 >= 0.7:
            grade = "优秀"
        elif avg_f1 >= 0.5:
            grade = "良好"
        elif avg_f1 >= 0.3:
            grade = "中等"
        else:
            grade = "需要改进"
        
        print(f"综合评级: {grade}")
        
        # 推荐系统分析
        print("\n推荐系统分析:")
        if avg_precision > avg_recall:
            print("- 推荐系统倾向于保守，推荐的商品质量较高但覆盖面较窄")
        elif avg_recall > avg_precision:
            print("- 推荐系统倾向于激进，推荐覆盖面广但精准度有待提高")
        else:
            print("- 推荐系统在准确率和召回率之间取得了良好平衡")
        
        # 算法说明
        print("\n算法说明:")
        print("- 使用基于用户的协同过滤 (User-based CF)")
        print("- 使用基于商品的协同过滤 (Item-based CF)")
        print("- 采用余弦相似度计算")
        print("- 评分归一化处理")
        print(f"- 加权融合 (alpha={recommender.alpha})")
        print("- 生命周期推荐增强")
        
        print("\n" + "="*60)
        
        # 保存报告
        save_report(avg_precision, avg_recall, avg_f1, len(precision_scores))
        
    else:
        print("错误：没有足够的数据进行评估")


def save_report(precision, recall, f1, user_count):
    """保存评估报告"""
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'evaluation_report.txt'
    )
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("推荐系统评估报告\n")
        f.write("="*60 + "\n\n")
        f.write(f"评估时间: {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"评估用户数: {user_count}\n\n")
        f.write("评估指标:\n")
        f.write(f"  准确率 (Precision): {precision:.4f} ({precision*100:.2f}%)\n")
        f.write(f"  召回率 (Recall):    {recall:.4f} ({recall*100:.2f}%)\n")
        f.write(f"  F1分数 (F1-Score):  {f1:.4f} ({f1*100:.2f}%)\n\n")
        
        if f1 >= 0.7:
            grade = "优秀"
        elif f1 >= 0.5:
            grade = "良好"
        elif f1 >= 0.3:
            grade = "中等"
        else:
            grade = "需要改进"
        
        f.write(f"综合评级: {grade}\n\n")
        f.write("算法说明:\n")
        f.write("- 基于用户的协同过滤 (User-based CF)\n")
        f.write("- 基于商品的协同过滤 (Item-based CF)\n")
        f.write("- 余弦相似度计算\n")
        f.write("- 评分归一化\n")
        f.write("- 加权融合 (alpha=0.5)\n")
        f.write("- 生命周期推荐增强\n")
        f.write("="*60 + "\n")
    
    print(f"\n评估报告已保存到: {report_path}")


if __name__ == '__main__':
    evaluate_recommender()

