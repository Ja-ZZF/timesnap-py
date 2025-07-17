import jieba.analyse

def extract_keywords(text: str, top_k: int = 5):
    keywords = jieba.analyse.textrank(
        text,
        topK=top_k,
        withWeight=False,
        allowPOS=('ns', 'n', 'vn', 'v')
    )
    return [kw for kw in keywords if len(kw) >= 2]
