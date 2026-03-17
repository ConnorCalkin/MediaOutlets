from bs4 import BeautifulSoup


def get_body_text(html: str) -> str:
    '''Extracts and returns the text content of the article element from the given HTML string.'''
    soup = BeautifulSoup(html, "html.parser")
    article = soup.article
    article = article.find_all("p", recursive=False) if article else []
    article_text = " ".join([p.get_text() for p in article]) if article else ""
    return article_text
