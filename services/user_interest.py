from sqlalchemy import text
from typing import List, Tuple
from db import engine

ACTION_WEIGHT = {
    'view': 0.5,
    'like': 1.0,
    'collect': 1.5,
    'share': 2.0,
    'comment': 2.0,
}

def calculate_user_interest_tags(user_id: int, top_k: int = 10) -> List[Tuple[str, float]]:
    with engine.connect() as conn:
        sql_action = text("""
            SELECT post_id, action_type
            FROM user_action
            WHERE user_id = :user_id
        """)
        actions = conn.execute(sql_action, {"user_id": user_id}).mappings().all()
        if not actions:
            return []

        post_ids = list({row['post_id'] for row in actions})
        if not post_ids:
            return []

        sql_tags = text(f"""
            SELECT pt.post_id, t.tag_id, t.name
            FROM post_tag pt
            JOIN tag t ON pt.tag_id = t.tag_id
            WHERE pt.post_id IN :post_ids
        """)

        post_ids_tuple = tuple(post_ids)
        post_tags = conn.execute(sql_tags, {"post_ids": post_ids_tuple}).mappings().all()

        post_to_tags = {}
        for row in post_tags:
            post_to_tags.setdefault(row['post_id'], []).append({'tag_id': row['tag_id'], 'tag_name': row['name']})

        tag_weights = {}
        for action in actions:
            w = ACTION_WEIGHT.get(action['action_type'], 0)
            tags = post_to_tags.get(action['post_id'], [])
            for tag in tags:
                tag_weights[tag['tag_name']] = tag_weights.get(tag['tag_name'], 0) + w

        sorted_tags = sorted(tag_weights.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:top_k]
