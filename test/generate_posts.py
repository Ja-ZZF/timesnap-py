from sqlalchemy import text
from sqlalchemy.engine import Engine
from db import engine  # 你已有的db配置文件

import random

USER_ID = 2
COVER_URL = "http://47.117.0.254:4000/uploads/posts/original/1752723248106-189845301.jpg"

titles = [
    "探索人工智能的未来趋势",
    "深度学习在图像识别中的应用",
    "区块链技术与金融安全",
    "云计算架构设计实践",
    "大数据分析方法论",
    "移动端性能优化经验分享",
    "前端工程化工具合集",
    "如何设计高可用系统",
    "微服务架构的挑战与实践",
    "数据库索引优化技巧",
    "5G时代的网络技术演进",
    "智能家居系统设计探讨",
    "自动驾驶技术的现状与未来",
    "自然语言处理中的预训练模型",
    "容器化技术在企业应用的推广",
    "数据可视化工具与方法",
    "物联网安全威胁及防护措施",
    "开源软件的商业模式解析",
    "区块链与数字货币监管政策",
    "人工智能伦理问题研究",
]


contents = [
    "人工智能技术不断发展，推动社会进步。",
    "深度学习模型在计算机视觉领域表现优异，应用广泛。",
    "区块链技术为金融行业带来了革命性的变化和挑战。",
    "云计算平台为企业提供了灵活高效的资源管理方案。",
    "大数据分析助力精准营销和科学决策，提升业务效能。",
    "移动端性能优化是提升用户体验的重要环节。",
    "前端工程化工具链极大地提升了开发效率和代码质量。",
    "设计高可用系统需要多层容错机制保障服务稳定。",
    "微服务架构解耦复杂系统，提升了扩展性与维护性。",
    "数据库索引设计合理能显著降低查询延迟和资源消耗。",
    "5G技术推动了网络速率和连接密度的飞跃式提升。",
    "智能家居系统结合了物联网和人工智能技术，实现自动化控制。",
    "自动驾驶技术融合传感器和深度学习，实现安全驾驶。",
    "预训练模型在自然语言处理任务中表现出色，提升理解能力。",
    "容器化技术帮助企业实现应用快速部署和弹性伸缩。",
    "数据可视化是理解复杂数据的有效方式，支持决策分析。",
    "物联网设备安全面临多种威胁，需加强防护策略。",
    "开源软件通过社区协作推动技术创新和生态繁荣。",
    "数字货币的监管政策影响区块链技术的发展路径。",
    "人工智能伦理问题涉及隐私、安全和公平，需持续关注。",
]


def insert_posts(num: int = 20):
    with engine.connect() as conn:
        sql = text("""
            INSERT INTO post (user_id, publish_time, title, content, cover_url)
            VALUES (:user_id, NOW(), :title, :content, :cover_url)
        """)
        for _ in range(num):
            title = random.choice(titles)
            content = random.choice(contents)
            conn.execute(sql, {
                "user_id": USER_ID,
                "title": title,
                "content": content,
                "cover_url": COVER_URL,
            })
        conn.commit()
        print(f"成功插入 {num} 条帖子。")

if __name__ == "__main__":
    insert_posts(30)  # 插入30条
