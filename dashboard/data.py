import pandas as pd
import streamlit as st
from boto3.dynamodb.conditions import Key, Attr
from connect import get_dynamo_table


# ── Keywords ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def get_top_keywords(limit=10):
    """Scans for keyword# rows and counts mentions per keyword."""
    table = get_dynamo_table()
    response = table.scan(FilterExpression=Attr('pk').begins_with('keyword#'))
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()
    df = pd.DataFrame(items)
    df['keyword'] = df['pk'].str.replace('keyword#', '', regex=False)
    df = df.groupby('keyword').size().reset_index(name='mention_count')
    return df.sort_values(by='mention_count', ascending=False).head(limit)


# ── Entities ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def get_top_entities(entity_type='PERSON', limit=10):
    """Scans entity# rows filtered by type (PERSON, ORG, etc.) and counts mentions."""
    table = get_dynamo_table()
    response = table.scan(
        FilterExpression=Attr('pk').begins_with(
            'entity#') & Attr('type').eq(entity_type)
    )
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()
    df = pd.DataFrame(items)
    df['entity'] = df['pk'].str.replace('entity#', '', regex=False)
    df = df.groupby('entity').size().reset_index(name='mention_count')
    return df.sort_values(by='mention_count', ascending=False).head(limit)


# ── Celebrity queries ────────────────────────────────────────────────────────

def _get_articles_for_entity(name: str) -> pd.DataFrame:
    """Shared helper: fetches all articles mentioning a given entity name."""
    table = get_dynamo_table()
    entity_response = table.query(
        KeyConditionExpression=Key('pk').eq(f"entity#{name}")
    )
    urls = [item['sk'] for item in entity_response.get('Items', [])]
    if not urls:
        return pd.DataFrame()
    articles = []
    for url in urls:
        resp = table.get_item(Key={'pk': url, 'sk': 'metadata'})
        if 'Item' in resp:
            articles.append(resp['Item'])
    if not articles:
        return pd.DataFrame()
    df = pd.DataFrame(articles)
    df['published_date'] = pd.to_datetime(df['published_date'])
    df['sentiment_label'] = df['sentiment'].apply(
        lambda x: x.get('label') if isinstance(x, dict) else None
    )
    df['sentiment_polarity'] = df['sentiment'].apply(
        lambda x: float(x.get('polarity', 0)) if isinstance(x, dict) else 0
    )
    return df


@st.cache_data(ttl=600)
def get_celebrity_mentions(name: str, start_date=None, end_date=None) -> pd.DataFrame:
    """Returns articles mentioning a celebrity, optionally filtered by date window."""
    df = _get_articles_for_entity(name)
    if df.empty:
        return df
    if start_date:
        df = df[df['published_date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['published_date'] <= pd.to_datetime(end_date)]
    return df.sort_values('published_date', ascending=False)


@st.cache_data(ttl=600)
def get_sentiment_over_time(name: str) -> pd.DataFrame:
    """Returns sentiment polarity over time for a specific celebrity."""
    df = _get_articles_for_entity(name)
    if df.empty:
        return df
    return df[['published_date', 'sentiment_polarity', 'sentiment_label', 'title', 'source']]\
        .sort_values('published_date')


@st.cache_data(ttl=600)
def compare_celebrities(names: list) -> pd.DataFrame:
    """Returns mention counts and avg sentiment for a list of celebrities for comparison."""
    rows = []
    for name in names:
        df = _get_articles_for_entity(name)
        if df.empty:
            rows.append(
                {'celebrity': name, 'mention_count': 0, 'avg_sentiment': 0})
        else:
            rows.append({
                'celebrity': name,
                'mention_count': len(df),
                'avg_sentiment': round(df['sentiment_polarity'].mean(), 3)
            })
    return pd.DataFrame(rows).sort_values('mention_count', ascending=False)


# ── Sources ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def get_articles_by_source() -> pd.DataFrame:
    """Scans metadata rows and groups by source."""
    table = get_dynamo_table()
    response = table.scan(FilterExpression=Attr('sk').eq('metadata'))
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()
    df = pd.DataFrame(items)
    return df.groupby('source').size().reset_index(name='article_count')\
        .sort_values('article_count', ascending=False)


@st.cache_data(ttl=600)
def get_sentiment_breakdown() -> pd.DataFrame:
    """Returns count of positive/negative/neutral articles across all articles."""
    table = get_dynamo_table()
    response = table.scan(FilterExpression=Attr('sk').eq('metadata'))
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()
    df = pd.DataFrame(items)
    df['sentiment_label'] = df['sentiment'].apply(
        lambda x: x.get('label') if isinstance(x, dict) else 'unknown'
    )
    return df.groupby('sentiment_label').size().reset_index(name='count')


# ── Test ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Top Keywords:")
    print(get_top_keywords())
    print("\nTop People:")
    print(get_top_entities('PERSON'))
    print("\nTop Orgs:")
    print(get_top_entities('ORG'))
    print("\nArticles by source:")
    print(get_articles_by_source())
    print("\nSentiment breakdown:")
    print(get_sentiment_breakdown())
    print("\nOliver Boot mentions:")
    print(get_celebrity_mentions('Oliver Boot'))
    print("\nSentiment over time:")
    print(get_sentiment_over_time('Oliver Boot'))
    print("\nComparison:")
    print(compare_celebrities(['Oliver Boot', 'Elon Musk']))
