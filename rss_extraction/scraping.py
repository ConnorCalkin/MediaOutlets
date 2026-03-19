from newspaper import Article


def get_body_text(url: str) -> str:
    """Downloads and extracts the article body text from a given URL."""
    article = Article(url)
    article.download()
    article.parse()
    return article.text
