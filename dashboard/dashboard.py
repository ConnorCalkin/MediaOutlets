import streamlit as st
from data import get_top_keywords, get_top_entities


def main():
    st.title("Media Outlet Dashboard")
    st.write("Welcome to the Media Outlet Dashboard! Here you can view insights and analytics about the articles we've ingested.")


def top_people():
    st.header("Top People Mentioned")
    df = get_top_entities('PERSON')
    if df.empty:
        st.write("No data available.")
    else:
        st.bar_chart(df.set_index('entity')['mention_count'])


def top_organizations():
    st.header("Top Organizations Mentioned")
    df = get_top_entities('ORG')
    if df.empty:
        st.write("No data available.")
    else:
        st.bar_chart(df.set_index('entity')['mention_count'])


def top_keywords():
    st.header("Top Keywords")
    df = get_top_keywords()
    if df.empty:
        st.write("No data available.")
    else:
        st.bar_chart(df.set_index('keyword')['mention_count'])


if __name__ == "__main__":
    main()
    top_people()
    top_organizations()
    top_keywords()
