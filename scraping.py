from bs4 import BeautifulSoup


def get_body_text(html: str) -> str:
    '''Extracts and returns the text content of the article element from the given HTML string.'''
    soup = BeautifulSoup(html, "html.parser")
    article = soup.article
    return article.get_text() if article else ""
