import pytest
from parsing import get_links_from_rss


class TestGetLinksFromRss:
    def test_get_links_from_rss(self):
        rss_content = '''<?xml version="1.0" encoding="UTF-8" ?>
        <rss version="2.0">
            <channel>
                <title>Example RSS Feed</title>
                <item>
                    <title>Article 1</title>
                    <link>http://example.com/article1</link>
                </item>
                <item>
                    <title>Article 2</title>
                    <link>http://example.com/article2</link>
                </item>
            </channel>
        </rss>'''

        expected_links = ['http://example.com/article1',
                          'http://example.com/article2']
        assert get_links_from_rss(rss_content) == expected_links

    def test_get_links_from_rss_no_items(self):
        rss_content = '''<?xml version="1.0" encoding="UTF-8" ?>
        <rss version="2.0">
            <channel>
                <title>Example RSS Feed</title>
            </channel>
        </rss>'''

        expected_links = []
        assert get_links_from_rss(rss_content) == expected_links

    def test_get_links_from_rss_malformed_xml(self):
        rss_content = '''<?xml version="1.0" encoding="UTF-8" ?>
        <rss version="2.0">
            <channel>
                <title>Example RSS Feed</title>
                <item>
                    <title>Article 1</title>
                    <link>http://example.com/article1</link>
                <!-- Missing closing tags -->
        '''

        with pytest.raises(Exception):
            get_links_from_rss(rss_content)

    def test_get_links_from_rss_links_not_in_item(self):
        rss_content = '''<?xml version="1.0" encoding="UTF-8" ?>
        <rss version="2.0">
            <channel>
                <title>Example RSS Feed</title>
                <link>http://example.com/article1</link>
                <link>http://example.com/article2</link>
            </channel>
        </rss>'''

        expected_links = []
        assert get_links_from_rss(rss_content) == expected_links
