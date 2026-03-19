import streamlit as st
import pandas as pd
from data import (
    get_sentiment_over_time,
    get_mentions_over_time,
    get_top_keywords,
    get_top_entities,
    get_articles_by_source,
    compare_celebrities
)

# --- Layout Configuration ---
st.set_page_config(page_title="Media Outlet Dashboard", layout="wide")


@st.cache_data(ttl=600)
def display_top_metrics():
    """Displays top organizations and keywords in two columns."""
    col1, col2 = st.columns(2)

    with col1:
        st.header("Top Organizations")
        df_org = get_top_entities('ORG')
        if not df_org.empty:
            st.bar_chart(df_org.set_index('entity')['mention_count'])
        else:
            st.info("No organization data found.")

    with col2:
        st.header("Top Keywords")
        df_key = get_top_keywords()
        if not df_key.empty:
            st.bar_chart(df_key.set_index('keyword')['mention_count'])
        else:
            st.info("No keyword data found.")


def display_sources():
    """Displays article distribution by source."""
    st.header("Articles by Source")
    df = get_articles_by_source()
    if not df.empty:
        # Using a pie chart for source distribution
        st.pie_chart(df.set_index('source')['article_count'])
    else:
        st.info("No source data available.")


def celebrity_section():
    """Handles the selection and detailed charts for a single celebrity."""
    st.header("Individual Celebrity Analysis")

    # Get top people for the dropdown
    df_people = get_top_entities('PERSON')
    if df_people.empty:
        st.warning("No celebrities found in the database.")
        return

    selected_celebrity = st.selectbox(
        "Select a celebrity to view details:",
        df_people['entity'].tolist()
    )

    if selected_celebrity:
        col1, col2 = st.columns(2)

        # 1. Mentions Over Time
        with col1:
            st.subheader(f"Mentions: {selected_celebrity}")
            m_df = get_mentions_over_time(selected_celebrity)
            if not m_df.empty:
                st.line_chart(m_df.set_index('date_only')['mention_count'])
            else:
                st.write("No mention trend data available.")

        # 2. Sentiment Over Time
        with col2:
            st.subheader(f"Sentiment Trend: {selected_celebrity}")
            s_df = get_sentiment_over_time(selected_celebrity)
            if not s_df.empty:
                st.line_chart(s_df.set_index('date_only')
                              ['sentiment_polarity'])
            else:
                st.write("No sentiment trend data available.")


def comparison_section():
    """Allows users to compare multiple celebrities side-by-side."""
    st.header("Celebrity Comparison")
    df_people = get_top_entities('PERSON')

    if not df_people.empty:
        selected_names = st.multiselect(
            "Select celebrities to compare:",
            df_people['entity'].tolist(),
            default=df_people['entity'].tolist()[:2]  # Default to top 2
        )

        if selected_names:
            comparison_df = compare_celebrities(selected_names)
            st.dataframe(comparison_df, use_container_width=True)

            # Optional: Visual comparison of mentions
            st.bar_chart(comparison_df.set_index('Celebrity')['Mentions'])


def main():
    st.title("📊 Media Outlet Dashboard")
    st.markdown("""
        Welcome to the **Media Outlet Dashboard**! 
        Analyze trends, sentiment, and mentions from ingested news articles.
    """)
    st.divider()

    # 1. Global Metrics
    display_top_metrics()
    st.divider()

    # 2. Source Distribution
    display_sources()
    st.divider()

    # 3. Individual Deep Dive
    celebrity_section()
    st.divider()

    # 4. Multi-Celebrity Comparison
    comparison_section()


if __name__ == "__main__":
    main()
