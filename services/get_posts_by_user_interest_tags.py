import random
from sqlalchemy import text
from typing import List, Tuple
from db import engine
from services.user_interest import calculate_user_interest_tags


def get_recommended_posts(user_id: int, num_posts: int = 20) -> List[int]:
    # 先计算兴趣标签及权重
    interest_tags = calculate_user_interest_tags(user_id, top_k=10)
    if not interest_tags:
        return []

    total_weight = sum(w for _, w in interest_tags)
    if total_weight == 0:
        return []

    with engine.connect() as conn:
        selected_post_ids = set()

        for tag_name, weight in interest_tags:
            # 按比例分配每个标签要获取的帖子数，至少1个
            count = max(1, int(num_posts * weight / total_weight))

            # 先查该标签帖子中，用户未操作过的帖子
            sql_unacted = text("""
                SELECT pt.post_id
                FROM post_tag pt
                JOIN tag t ON pt.tag_id = t.tag_id
                LEFT JOIN user_action ua ON ua.post_id = pt.post_id AND ua.user_id = :user_id
                WHERE t.name = :tag_name
                  AND ua.action_id IS NULL
                AND pt.post_id NOT IN :excluded_post_ids
                ORDER BY RAND()
                LIMIT :limit_count
            """)
            excluded = tuple(selected_post_ids) if selected_post_ids else (-1,)
            unacted_posts = conn.execute(sql_unacted, {
                "user_id": user_id,
                "tag_name": tag_name,
                "excluded_post_ids": excluded,
                "limit_count": count
            }).fetchall()
            unacted_post_ids = [row[0] for row in unacted_posts]
            selected_post_ids.update(unacted_post_ids)

            # 如果不够，补充其他帖子
            if len(unacted_post_ids) < count:
                remaining = count - len(unacted_post_ids)
                sql_all = text("""
                    SELECT pt.post_id
                    FROM post_tag pt
                    JOIN tag t ON pt.tag_id = t.tag_id
                    WHERE t.name = :tag_name
                      AND pt.post_id NOT IN :excluded_post_ids
                    ORDER BY RAND()
                    LIMIT :limit_count
                """)
                excluded = tuple(selected_post_ids) if selected_post_ids else (-1,)
                all_posts = conn.execute(sql_all, {
                    "tag_name": tag_name,
                    "excluded_post_ids": excluded,
                    "limit_count": remaining
                }).fetchall()
                all_post_ids = [row[0] for row in all_posts]
                selected_post_ids.update(all_post_ids)

        # 最终随机排序，返回最多num_posts个帖子id
        result = list(selected_post_ids)
        random.shuffle(result)
        return result[:num_posts]
