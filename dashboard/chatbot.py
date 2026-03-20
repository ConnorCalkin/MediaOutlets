import requests
import streamlit as st

API_URL = "https://jpqtbns0w5.execute-api.eu-west-2.amazonaws.com/query"


def chat_bot():
    # user input
    prompt = st.chat_input("Ask something...")

    # store chat history for session
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display previous messages of session
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt:
        # show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # call API
        response = requests.post(
            API_URL,
            json={"question": prompt}
        )

        if response.status_code == 200:
            data = response.json()
            print(data)
            answer = data["answer"]

            # show assistant response
            with st.chat_message("assistant"):
                st.write(answer)

                # sources
                if data.get("sources"):
                    st.write("**Sources:**")
                    for s in data["sources"]:
                        st.link_button(s["title"], url=s["url"])

            # save response
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        else:
            st.error("API request failed")
