import pandas as pd
import streamlit as st
from boto3.dynamodb.conditions import Key, Attr
from connect import get_dynamo_table


# warning scans the table which is expensive
# in production, we would want to use more tables to avoid full scans.
@st.cache_data(ttl=600)
def get_top_keywords(limit=10):
    """Queries the DB for top keywords and returns a clean DataFrame."""
    table = get_dynamo_table()
    response = table.scan(
        FilterExpression=Attr('pk').begins_with('keyword#')
    )
    items = response.get('Items', [])
    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)
    # Extract keyword name from pk (e.g. "keyword#Electric Cars" -> "Electric Cars")
    df['keyword'] = df['pk'].str.replace('keyword#', '', regex=False)
    # Count how many article URLs (sk) each keyword appears in
    df = df.groupby('keyword').size().reset_index(name='mention_count')
    return df.sort_values(by='mention_count', ascending=False).head(limit)


# this does not require scans
def get_celebrity_mentions(name):
    """Queries the DB for a specific entity and returns a clean DataFrame."""
    table = get_dynamo_table()

    # 1. Get URLs from Entity rows
    entity_response = table.query(
        KeyConditionExpression=Key('pk').eq(f"entity#{name}")
    )
    urls = [item['sk'] for item in entity_response.get('Items', [])]

    if not urls:
        return pd.DataFrame()

    # 2. Get Metadata for those URLs
    articles = []
    for url in urls:
        resp = table.get_item(Key={'pk': url, 'sk': 'metadata'})
        if 'Item' in resp:
            articles.append(resp['Item'])

    df = pd.DataFrame(articles)
    if not df.empty:
        df['published_date'] = pd.to_datetime(df['published_date'])
    return df


# test the functions
if __name__ == "__main__":
    print("Top Keywords:")
    # print(get_top_keywords().head())

    print("\nMentions for 'Elon Musk':")
    print(get_celebrity_mentions('Elon Musk'))
