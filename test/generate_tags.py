from sqlalchemy import text
from db import engine  # 你已有的数据库连接配置
from services.keyword_extractor import extract_keywords


def process_all_posts(top_k: int = 5):
    with engine.connect() as conn:
        # 读取所有帖子id、标题和内容
        sql_posts = text("SELECT post_id, title, content FROM post")
        posts = conn.execute(sql_posts).mappings().all()  # 用mappings()返回字典

        for post in posts:
            post_id = post['post_id']
            combined_text = (post['title'] or '') + ' ' + (post['content'] or '')
            keywords = extract_keywords(combined_text, top_k)

            for kw in keywords:
                # 查询标签是否已存在，mappings()返回字典
                sql_tag = text("SELECT tag_id FROM tag WHERE name = :name")
                tag_row = conn.execute(sql_tag, {'name': kw}).mappings().fetchone()

                if tag_row:
                    tag_id = tag_row['tag_id']
                else:
                    # 标签不存在，插入新标签
                    sql_insert_tag = text("INSERT INTO tag (name) VALUES (:name)")
                    result = conn.execute(sql_insert_tag, {'name': kw})
                    # 获取新插入标签的id
                    tag_id = result.lastrowid

                # 检查post_tag是否已有关联，mappings()返回字典
                sql_check = text("""
                    SELECT 1 FROM post_tag 
                    WHERE post_id = :post_id AND tag_id = :tag_id
                """)
                exists = conn.execute(sql_check, {'post_id': post_id, 'tag_id': tag_id}).fetchone()

                if not exists:
                    sql_insert_post_tag = text("""
                        INSERT INTO post_tag (post_id, tag_id) VALUES (:post_id, :tag_id)
                    """)
                    conn.execute(sql_insert_post_tag, {'post_id': post_id, 'tag_id': tag_id})

        conn.commit()
    print("全部帖子标签处理完成。")

if __name__ == '__main__':
    process_all_posts()
