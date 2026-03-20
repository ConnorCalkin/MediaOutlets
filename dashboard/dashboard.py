import streamlit as st
import pandas as pd
import plotly.express as px
from data import (
    get_top_entities,
    get_bottom_entities,
    get_top_keywords,
    get_sentiment_for_entity,
    compare_celebrities
)

# Page Config
st.set_page_config(page_title="Media Outlets & News Summary", layout="wide")

st.title("📰 Media Outlets & News Summary Dashboard")
st.markdown("Analyzing sentiment and trends across entities and keywords.")

# --- Sidebar Controls ---
st.sidebar.header("Settings")
limit = st.sidebar.slider("Number of entities to show", 5, 20, 10)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(
    ["📊 Global Overview", "🔍 Entity Analysis", "⚔️ Comparison"])

# --- Tab 1: Global Overview ---
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Top {limit} Entities (Positive Sentiment)")
        top_df = get_top_entities(limit=limit)
        if not top_df.empty:
            fig_top = px.bar(
                top_df, x='Avg Sentiment', y='Entity',
                orientation='h', color='Avg Sentiment',
                color_continuous_scale='Greens',
                text_auto='.2f'
            )
            fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("No data found.")

    with col2:
        st.subheader(f"Bottom {limit} Entities (Negative Sentiment)")
        bottom_df = get_bottom_entities(limit=limit)
        if not bottom_df.empty:
            fig_bottom = px.bar(
                bottom_df, x='Avg Sentiment', y='Entity',
                orientation='h', color='Avg Sentiment',
                color_continuous_scale='Reds',
                text_auto='.2f'
            )
            fig_bottom.update_layout(
                yaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig_bottom, use_container_width=True)

    st.divider()

    st.subheader("Trending Keywords")
    keywords_df = get_top_keywords(limit=15)
    if not keywords_df.empty:
        fig_keys = px.treemap(
            keywords_df, path=['keyword'], values='mention_count',
            color='mention_count', color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_keys, use_container_width=True)

# --- Tab 2: Entity Analysis ---
with tab2:
    st.subheader("Deep Dive into Specific Entity")
    search_name = st.text_input(
        "Enter Entity Name (e.g., KPMG,Truss):", "KPMG")

    if search_name:
        entity_df = get_sentiment_for_entity(search_name)

        if not entity_df.empty:
            # Metrics
            m1, m2 = st.columns(2)
            avg_pol = entity_df['sentiment_polarity'].mean()
            m1.metric("Average Polarity", f"{avg_pol:.2f}")
            m2.metric("Total Articles", len(entity_df))

            # Sentiment Timeline
            st.markdown(f"**Sentiment Trend for {search_name}**")
            fig_line = px.line(
                entity_df, x='published_at', y='sentiment_polarity',
                hover_data=['title'], markers=True,
                labels={'sentiment_polarity': 'Sentiment Score',
                        'published_at': 'Date'}
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Data Table
            st.markdown("**Recent Articles**")
            st.dataframe(
                entity_df[['published_at', 'title', 'sentiment_label', 'url']],
                use_container_width=True,
                column_config={
                    "url": st.column_config.LinkColumn(
                        "Article Link",
                        help="Click to open the full article",
                        validate="^https?://",
                        # This makes every link say "Open Article" instead of the long URL
                        display_text="Open Article"
                    )
                },
                hide_index=True
            )

# --- Tab 3: Comparison ---
with tab3:
    st.subheader("Compare Multiple Entities")
    compare_list = st.multiselect(
        "Select entities to compare:",
        options=top_df['Entity'].tolist(
        ) + bottom_df['Entity'].tolist() if not top_df.empty else [],
        default=[]
    )

    if compare_list:
        comp_df = compare_celebrities(compare_list)
        fig_comp = px.scatter(
            comp_df, x='Celebrity', y='Avg Sentiment',
            size=[10]*len(comp_df), color='Avg Sentiment',
            color_continuous_scale='RdYlGn', range_color=[-1, 1]
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        st.table(comp_df)
    else:
        st.info("Please select entities from the dropdown to compare them.")
