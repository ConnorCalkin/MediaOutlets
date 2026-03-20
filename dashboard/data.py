import pandas as pd
import streamlit as st
from boto3.dynamodb.conditions import Key, Attr
from connect import get_dynamo_table
from decimal import Decimal


# ── Shared Helper ─────────────────────────────────────────────────────────────
def _get_articles_for_entity(name: str) -> pd.DataFrame:
    """Fetches all articles mentioning a given entity name and ensures clean columns."""
    table = get_dynamo_table()

    # 1. Get the list of URLs (stored as 'sk') associated with this entity 'pk'
    entity_response = table.query(
        KeyConditionExpression=Key('pk').eq(f"entity#{name}")
    )
    items = entity_response.get('Items', [])
    if not items:
        return pd.DataFrame()

    # Extract the URLs from the 'sk' column of the entity mapping
    urls = [item['sk'] for item in items]

    # 2. Fetch the metadata for each URL
    articles = []
    for url in urls:
        # We look up the metadata using the URL as the 'pk'
        resp = table.get_item(Key={'pk': url, 'sk': 'metadata'})
        if 'Item' in resp:
            item = resp['Item']

            # --- CRITICAL FIX: Inject the URL back into the item ---
            # DynamoDB doesn't repeat the 'pk' inside the attributes,
            # so we manually add it so Pandas can see it as a column.
            item['url'] = url

            articles.append(item)

    if not articles:
        return pd.DataFrame()

    # 3. Create DataFrame
    df = pd.DataFrame(articles)

    # 4. Enforce presence of critical columns (prevents KeyError)
    expected_cols = ['title', 'url', 'published_date', 'sentiment']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # 5. Robust Parsing of Dates
    df['published_at'] = pd.to_datetime(df['published_date'], errors='coerce')
    # Fill missing dates with a placeholder to prevent sorting crashes
    df['published_at'] = df['published_at'].fillna(pd.Timestamp('1970-01-01'))

    # 6. Robust Parsing of Sentiment
    def _parse_sentiment(x):
        # Handle cases where sentiment is stored as a string representation of a dict
        if isinstance(x, str):
            try:
                x = ast.literal_eval(x)
            except:
                return 'Unknown', 0.0

        if isinstance(x, dict):
            label = x.get('label', 'Unknown')
            # Convert Boto3 Decimal to float so Plotly/Streamlit can read it
            polarity = float(x.get('polarity', 0.0))
            return label, polarity

        return 'Unknown', 0.0

    # Apply the parser and expand into two new columns
    sentiment_results = df['sentiment'].apply(_parse_sentiment)
    df[['sentiment_label', 'sentiment_polarity']] = pd.DataFrame(
        sentiment_results.tolist(), index=df.index
    )

    return df
    # ── Analytics Functions ───────────────────────────────────────────────────────


def get_sentiment_for_entity(name: str) -> pd.DataFrame:
    """Returns a DataFrame of articles mentioning the entity with sentiment details."""
    df = _get_articles_for_entity(name)
    if df.empty:
        return pd.DataFrame()

    return df[[
        'title', 'url', 'published_at', 'sentiment_label', 'sentiment_polarity'
    ]].sort_values('published_at', ascending=False).reset_index(drop=True)


def compare_celebrities(names: list) -> pd.DataFrame:
    """Returns a comparison table of avg sentiment for multiple entities."""
    results = []
    for name in names:
        df = _get_articles_for_entity(name)
        avg = df['sentiment_polarity'].mean() if not df.empty else 0.0
        results.append({'Celebrity': name, 'Avg Sentiment': round(avg, 4)})

    return pd.DataFrame(results).sort_values('Avg Sentiment', ascending=False)


# ── Scan-based Functions ──────────────────────────────────────────────────────
def get_top_keywords(limit: int = 10) -> pd.DataFrame:
    """Returns the most frequently mentioned keywords."""
    table = get_dynamo_table()

    response = table.scan(
        FilterExpression=Attr('pk').begins_with('keyword#')
    )
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)
    df['keyword'] = df['pk'].str.replace('keyword#', '', regex=False)

    return (
        df.groupby('keyword')
        .size()
        .reset_index(name='mention_count')
        .sort_values('mention_count', ascending=False)
        .head(limit)
    )


@st.cache_data(ttl=3600)
def get_top_entities(limit: int = 10) -> pd.DataFrame:
    """
    Returns entities with the highest average sentiment polarity.
    Scans for entity# rows, groups by entity name, then fetches
    article sentiment for each unique entity.
    """
    table = get_dynamo_table()

    response = table.scan(
        FilterExpression=Attr('pk').begins_with('entity#')
    )
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()

    # Extract unique entity names from PKs like "entity#TikTok"
    entity_names = list({
        item['pk'].replace('entity#', '', 1)
        for item in items
    })

    results = []
    for name in entity_names:
        df = _get_articles_for_entity(name)
        if not df.empty:
            results.append({
                'Entity': name,
                'Article Count': len(df),
                'Avg Sentiment': round(df['sentiment_polarity'].mean(), 4),
            })

    if not results:
        return pd.DataFrame()

    return (
        pd.DataFrame(results)
        .sort_values('Avg Sentiment', ascending=False)
        .head(limit)
        .reset_index(drop=True)
    )


@st.cache_data(ttl=3600)
def get_bottom_entities(limit: int = 10) -> pd.DataFrame:
    """
    Returns entities with the lowest average sentiment polarity.
    """
    table = get_dynamo_table()

    response = table.scan(
        FilterExpression=Attr('pk').begins_with('entity#')
    )
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()

    # Extract unique entity names from PKs like "entity#TikTok"
    entity_names = list({
        item['pk'].replace('entity#', '', 1)
        for item in items
    })

    results = []
    for name in entity_names:
        df = _get_articles_for_entity(name)
        if not df.empty:
            results.append({
                'Entity': name,
                'Article Count': len(df),
                'Avg Sentiment': round(df['sentiment_polarity'].mean(), 4),
            })

    if not results:
        return pd.DataFrame()

    return (
        pd.DataFrame(results)
        .sort_values('Avg Sentiment', ascending=True)
        .head(limit)
        .reset_index(drop=True)
    )


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # print("=== Top Entities by Sentiment ===")
    # print(get_top_entities())

    # print("\n=== Bottom Entities by Sentiment ===")
    # print(get_bottom_entities())

    # print("\n=== Top Keywords ===")
    # print(get_top_keywords())\

    print(get_sentiment_for_entity("KPMG"))
    pass
