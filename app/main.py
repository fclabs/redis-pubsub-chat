import streamlit as st
from topics import get_topics
from typing import List, Tuple, Optional
from users import UserConversation


class StopRender(Exception): ...


@st.fragment(run_every=0.5)
def draw_chats(user_conversation: UserConversation):
    for message in user_conversation.messages:
        st.chat_message(name=message["user"]).write(message["message"])


chat_users: List[Optional[UserConversation]] = []

# Recover state
if "chat_users" in st.session_state:
    chat_users = st.session_state["chat_users"]
else:
    st.session_state["chat_users"] = chat_users = []

st.set_page_config(layout="wide")
st.title("Simple Chat App using Redis Pub/Sub")
st.button("Add Chat", on_click=lambda: chat_users.append(None))

col_panes = st.columns(len(chat_users) + 1)

for i in range(len(col_panes) - 1):
    try:
        with col_panes[i]:

            # Check if the user is set
            if (cu := chat_users[i]) is None:
                # User not created
                username = st.text_input("Username:", value="", key=f"username_{i}")
                if username:
                    chat_users[i] = (cu := UserConversation(username=username))
                    st.rerun()

            if cu:
                topics = get_topics()
                topic = st.selectbox("Topic", topics, key=f"topic_{i}")
                if cu.topic != topic:
                    cu.set_topic(topic)

                draw_chats(user_conversation=cu)

                content = st.chat_input("Please enter your message", key=f"user_input_{i}")
                if content:
                    cu.publish_message(content)

                # Update session
                st.session_state["chat_users"] = chat_users

    except StopRender:
        pass
