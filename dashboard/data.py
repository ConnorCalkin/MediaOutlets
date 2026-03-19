import pandas as pd
import streamlit as st
from boto3.dynamodb.conditions import Key, Attr
from connect import get_dynamo_table

# ── Shared Helper (The most important fix) ──────────────────────────────────


def _get_articles_for_entity(name: str) -> pd.DataFrame:
    """Fetches all articles mentioning a given entity name."""
    table = get_dynamo_table()

    # Use Query for efficiency (requires PK to be exactly 'entity#Name')
    entity_response = table.query(
        KeyConditionExpression=Key('pk').eq(f"entity#{name}")
    )

    items = entity_response.get('Items', [])
    if not items:
        return pd.DataFrame()

    # Extract the URLs from the Sort Key (sk) of the entity rows
    urls = [item['sk'] for item in items]

    articles = []
    for url in urls:
        # Fetch the actual metadata for each article URL
        resp = table.get_item(Key={'pk': url, 'sk': 'metadata'})
        if 'Item' in resp:
            articles.append(resp['Item'])

    if not articles:
        return pd.DataFrame()

    df = pd.DataFrame(articles)

    # Standardize Dates: Strip time so we can group by day
    df['published_at'] = pd.to_datetime(df['published_date'])
    df['date_only'] = df['published_at'].dt.date

    # Handle nested sentiment dictionary
    df['sentiment_label'] = df['sentiment'].apply(
        lambda x: x.get('label') if isinstance(x, dict) else 'Unknown'
    )
    df['sentiment_polarity'] = df['sentiment'].apply(
        lambda x: float(x.get('polarity', 0)) if isinstance(x, dict) else 0.0
    )
    return df

# ── Refined Analytics Functions ──────────────────────────────────────────────


def get_mentions_over_time(celebrity: str):
    """Returns a DataFrame with counts per day."""
    df = _get_articles_for_entity(celebrity)
    if df.empty:
        # Return empty DF with expected columns to prevent dashboard crashes
        return pd.DataFrame(columns=['date_only', 'mention_count'])

    # Group by the date (ignoring exact time)
    stats = df.groupby('date_only').size().reset_index(name='mention_count')
    return stats.sort_values('date_only')


def get_sentiment_over_time(name: str):
    """Returns average sentiment polarity per day for a specific celebrity."""
    df = _get_articles_for_entity(name)
    if df.empty:
        return pd.DataFrame(columns=['date_only', 'sentiment_polarity'])

    # Group by date and take the mean polarity
    stats = df.groupby('date_only')['sentiment_polarity'].mean().reset_index()
    return stats.sort_values('date_only')


def compare_celebrities(names: list):
    """Returns a comparison table for multiple celebrities."""
    results = []
    for name in names:
        df = _get_articles_for_entity(name)
        if not df.empty:
            results.append({
                'Celebrity': name,
                'Mentions': len(df),
                'Avg Sentiment': df['sentiment_polarity'].mean()
            })
        else:
            results.append(
                {'Celebrity': name, 'Mentions': 0, 'Avg Sentiment': 0})
    return pd.DataFrame(results).sort_values(by='Mentions', ascending=False)

# ── Existing Scans (Optimized) ───────────────────────────────────────────────


def get_top_keywords(limit=10):
    table = get_dynamo_table()
    # Scan for items where PK starts with keyword#
    response = table.scan(FilterExpression=Attr('pk').begins_with('keyword#'))
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)
    df['keyword'] = df['pk'].str.replace('keyword#', '', regex=False)
    return df.groupby('keyword').size().reset_index(name='mention_count')\
             .sort_values('mention_count', ascending=False).head(limit)


def get_top_entities(entity_type='PERSON', limit=10):
    """
    Scans all entity rows and returns a DataFrame of names and their total mention counts.
    """
    table = get_dynamo_table()

    # 1. Scan for all rows that are entities of a specific type
    # We filter by 'type' (e.g., PERSON or ORG)
    response = table.scan(
        FilterExpression=Attr('pk').begins_with(
            'entity#') & Attr('type').eq(entity_type)
    )
    items = response.get('Items', [])

    if not items:
        return pd.DataFrame(columns=['entity', 'mention_count'])

    # 2. Convert to DataFrame
    df = pd.DataFrame(items)

    # 3. Clean the 'pk' column to get just the name (remove 'entity#')
    df['entity'] = df['pk'].str.replace('entity#', '', regex=False)

    # 4. Group by the name and count the occurrences
    # Each row in DynamoDB represents one mention in one article
    counts = df.groupby('entity').size().reset_index(name='mention_count')

    # 5. Sort by highest mentions and clean the index
    return counts.sort_values(by='mention_count', ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    # Example usage for testing
    print(get_top_entities())
    # print(get_mentions_over_time("Celebrity A"))
    # print(get_sentiment_over_time("Celebrity A"))
    # print(compare_celebrities(["Celebrity A", "Celebrity B"]))
