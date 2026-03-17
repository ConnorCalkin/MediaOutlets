import pytest
from scraping import get_body_text


class TestGetBodyText:
    def test_get_body_text(self):
        html = '''<html><body><article>This is the article text.</article></body></html>'''
        expected_text = "This is the article text."
        assert get_body_text(html) == expected_text

    def test_get_body_text_no_article(self):
        html = '''<html><body><div>No article here.</div></body></html>'''
        expected_text = ""
        assert get_body_text(html) == expected_text

    def test_get_body_text_empty_html(self):
        html = ''
        expected_text = ""
        assert get_body_text(html) == expected_text

    def test_get_body_text_malformed_html(self):
        html = '''<html><body><article>This is the article text.</article></body>'''
        expected_text = "This is the article text."
        assert get_body_text(html) == expected_text
