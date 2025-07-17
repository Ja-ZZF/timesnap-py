import random
from sqlalchemy import text
from typing import List
from db import engine
from services.user_interest import calculate_user_interest_tags


def get_recommended_posts(user_id: int, num_posts: int = 20, is_video: bool = None) -> List[int]:  # ✅ 新增 is_video 参数
    interest_tags = calculate_user_interest_tags(user_id, top_k=10)
    if not interest_tags:
        return []

    total_weight = sum(w for _, w in interest_tags)
    if total_weight == 0:
        return []

    with engine.connect() as conn:
        selected_post_ids = set()

        for tag_name, weight in interest_tags:
            count = max(1, int(num_posts * weight / total_weight))

            sql_unacted = text(f"""   -- ✅ 用 f-string 以动态拼接 is_video 条件
                SELECT pt.post_id
                FROM post_tag pt
                JOIN tag t ON pt.tag_id = t.tag_id
                JOIN post p ON p.post_id = pt.post_id  -- ✅ 新增：联表 post，便于筛选 is_video
                LEFT JOIN user_action ua ON ua.post_id = pt.post_id AND ua.user_id = :user_id
                WHERE t.name = :tag_name
                  AND ua.action_id IS NULL
                  AND pt.post_id NOT IN :excluded_post_ids
                  {"AND p.is_video = :is_video" if is_video is not None else ""}  -- ✅ 可选的 is_video 条件
                ORDER BY RAND()
                LIMIT :limit_count
            """)

            excluded = tuple(selected_post_ids) if selected_post_ids else (-1,)
            params = {
                "user_id": user_id,
                "tag_name": tag_name,
                "excluded_post_ids": excluded,
                "limit_count": count
            }
            if is_video is not None:    # ✅ 参数补充
                params["is_video"] = is_video

            unacted_posts = conn.execute(sql_unacted, params).fetchall()
            unacted_post_ids = [row[0] for row in unacted_posts]
            selected_post_ids.update(unacted_post_ids)

            if len(unacted_post_ids) < count:
                remaining = count - len(unacted_post_ids)
                sql_all = text(f"""   -- ✅ 用 f-string 动态拼接 is_video 条件
                    SELECT pt.post_id
                    FROM post_tag pt
                    JOIN tag t ON pt.tag_id = t.tag_id
                    JOIN post p ON p.post_id = pt.post_id  -- ✅ 新增：联表 post
                    WHERE t.name = :tag_name
                      AND pt.post_id NOT IN :excluded_post_ids
                      {"AND p.is_video = :is_video" if is_video is not None else ""}  -- ✅ 可选的 is_video 条件
                    ORDER BY RAND()
                    LIMIT :limit_count
                """)

                params_all = {
                    "tag_name": tag_name,
                    "excluded_post_ids": excluded,
                    "limit_count": remaining
                }
                if is_video is not None:    # ✅ 参数补充
                    params_all["is_video"] = is_video

                all_posts = conn.execute(sql_all, params_all).fetchall()
                all_post_ids = [row[0] for row in all_posts]
                selected_post_ids.update(all_post_ids)

        result = list(selected_post_ids)
        random.shuffle(result)
        return result[:num_posts]
