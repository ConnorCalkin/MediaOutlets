import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import plotly.express as px
from data import (
    get_top_entities,
    get_bottom_entities,
    get_top_keywords,
    get_sentiment_for_entity,
    compare_celebrities,
    get_entities
)
from chatbot import chat_bot


def chat_button():
    '''
    Renders a fixed-position chat button that
    opens a popover with the chatbot when clicked.'''
    with stylable_container(
        key="green_popover",
        css_styles="""
            button {
                width: 70px;
                height: 70px;
                background-color: white;
                color: red;
                border-radius: 5px;
                white-space: nowrap;
                position: fixed;
                top: 70px;
                right: 20px;
                z-index: 1000;
                overscroll-behavior: contain;
            }
            #bui2 {
                position: fixed;
                top: 140px;
                left: calc(100% - 620px);
                z-index: 1001;
                width: 500px;
                overscroll-behavior: contain !important;
            }
            """,
    ):
        with st.popover("Chat"):
            chat_bot()


def display_top_entities(top_entities_df=None):
    '''
    Graph showing the entities with the highest average sentiment polarity,
    sorted from most positive to least positive.
    '''
    st.subheader(f"Entities (Positive Sentiment)")
    if top_entities_df is not None and not top_entities_df.empty:
        fig_top = px.bar(
            top_entities_df, x='Avg Sentiment', y='Entity',
            orientation='h', color='Avg Sentiment',
            color_continuous_scale='Greens',
            text_auto='.2f'
        )
        fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("No data found.")


def display_bottom_entities(bottom_entities_df=None):
    '''
    Graph showing the entities with the lowest average sentiment polarity,
    sorted from most negative to least negative.
    '''
    st.subheader(f"Entities (Negative Sentiment)")
    if bottom_entities_df is not None and not bottom_entities_df.empty:
        fig_bottom = px.bar(
            bottom_entities_df, x='Avg Sentiment', y='Entity',
            orientation='h', color='Avg Sentiment',
            color_continuous_scale='Reds',
            text_auto='.2f'
        )
        fig_bottom.update_layout(
            yaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_bottom, use_container_width=True)


def display_top_keywords(top_keywords_df: pd.DataFrame = None):
    '''
    Graph showing the keywords with the highest average sentiment polarity,
    sorted from most positive to least positive.
    '''
    st.subheader("Trending Keywords")
    st.header("Settings")
    st.slider("Number of keywords to show",
              5, 20, 10, key="keyword_limit")

    if top_keywords_df is not None and not top_keywords_df.empty:
        fig_keys = px.treemap(
            top_keywords_df, path=['keyword'], values='mention_count',
            color='mention_count', color_continuous_scale='Blues',
        )
        st.plotly_chart(fig_keys, use_container_width=True)


def global_overview(top_df: pd.DataFrame = None, bottom_df: pd.DataFrame = None, top_keywords_df: pd.DataFrame = None):
    '''
    Displays the global overview tab with top entities, bottom entities, and top keywords.
    '''

    col1, col2 = st.columns(2)

    with col1:
        display_top_entities(top_df)
    with col2:
        display_bottom_entities(bottom_df)
    st.divider()
    display_top_keywords(top_keywords_df)


def header():
    '''Renders the header of the dashboard.'''
    st.title("📰 Media Outlets & News Summary Dashboard")
    st.markdown("Analyzing sentiment and trends across entities and keywords.")


def entity_analysis():
    '''
    Allows users to input an entity name and see a deep dive
      analysis of sentiment trends and related articles for that entity.
    '''
    st.subheader("Deep Dive into Specific Entity")

    search_name = st.selectbox(
        "Select an entity to analyze:",
        options=get_entities()['entity'].unique().tolist()
    )

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


def comparison(entities_df: pd.DataFrame = None):
    '''
    Allows users to select multiple entities from the top and bottom lists
      and compare their average sentiment scores in a scatter plot.
    '''
    st.subheader("Compare Multiple Entities")

    # Multiselect to select relevant entities
    compare_list = st.multiselect(
        "Select entities to compare:",
        options=entities_df['entity'].tolist(
        ) if entities_df is not None else [],
        default=[]
    )

    # chart comparison of entities as well as table comparison
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


def body():
    '''Fetches data and renders the main body of the dashboard, including all tabs and visualizations.'''
    # --- Get Data ---

    top_df = get_top_entities()
    bottom_df = get_bottom_entities()
    if 'keyword_limit' not in st.session_state:
        st.session_state.keyword_limit = 10
    top_keywords_df = get_top_keywords(limit=st.session_state.keyword_limit)

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(
        ["📊 Global Overview", "🔍 Entity Analysis", "⚔️ Comparison"])
    with tab1:
        global_overview(top_df, bottom_df, top_keywords_df)
    with tab2:
        entity_analysis()
    with tab3:
        entities_df = get_entities()
        comparison(entities_df)


def create_dashboard():
    '''Main function to create the Streamlit dashboard, including header, sidebar, body, and chat button.'''
    st.set_page_config(
        page_title="Media Outlets & News Summary", layout="wide")
    chat_button()
    header()
    body()


if __name__ == "__main__":
    create_dashboard()
