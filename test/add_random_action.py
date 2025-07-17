import random
from datetime import datetime, timedelta
from sqlalchemy import text
from db import engine  # 你已有的数据库连接配置

USER_ID = 14
ACTION_TYPES = ['view', 'like', 'collect', 'share', 'comment']

def add_random_user_actions(num_actions=50):
    with engine.connect() as conn:
        # 1. 查询所有帖子ID
        sql_posts = text("SELECT post_id FROM post")
        post_rows = conn.execute(sql_posts).mappings().all()
        post_ids = [row['post_id'] for row in post_rows]
        if not post_ids:
            print("没有可用帖子，无法添加用户行为。")
            return

        sql_insert = text("""
            INSERT INTO user_action (user_id, post_id, action_type, created_at)
            VALUES (:user_id, :post_id, :action_type, :created_at)
        """)

        for _ in range(num_actions):
            post_id = random.choice(post_ids)
            action_type = random.choice(ACTION_TYPES)
            # 随机生成过去30天内的时间
            created_at = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))

            conn.execute(sql_insert, {
                'user_id': USER_ID,
                'post_id': post_id,
                'action_type': action_type,
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        conn.commit()
        print(f"成功为用户 {USER_ID} 添加了 {num_actions} 条随机行为。")

if __name__ == "__main__":
    add_random_user_actions(50)
