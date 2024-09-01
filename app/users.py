import time
from typing import Optional, List, TypedDict
from redis import Redis
import json
import time
import os


def get_timestamp() -> int:
    return int(time.time())


class ChatMessage(TypedDict):
    user: str
    message: str
    timestamp: int


class UserConversation:
    def __init__(self, username: str):
        self.username = username
        self.topic: Optional[str] = None
        self.messages: List[ChatMessage] = []
        self.pubsub = None
        self.redis_client = Redis(os.getenv("REDIS_URL", "localhost"))

    def publish_message(self, content: str) -> None:
        if self.topic:
            self.messages.append(message := ChatMessage(user=self.username, message=content, timestamp=get_timestamp()))
            self.redis_client.publish(channel=self.topic, message=json.dumps(message).encode())

    def clean_messages(self) -> None:
        self.messages = []

    def set_topic(self, topic: str) -> None:
        self.topic = topic
        self.clean_messages()
        self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(**{self.topic: self.on_new_message})
        self.pubsub.run_in_thread(sleep_time=0.5)

    def on_new_message(self, message):
        if message['type'] == 'message':
            chat_item = ChatMessage(**json.loads(message['data'].decode()))
            print(f"Received: chat_item: ", chat_item)
            if chat_item['user'] != self.username:
                self.messages.append(chat_item)

    def update_chat_container(self, container):
        container.write(f"Username: {self.username}")

        # Draw chat messages for this topic
        for chat_item in cu.messages:
            with st.chat_message(name=chat_item["user"]):
                st.write(chat_item["message"])

        prompt = st.chat_input(key=f"message_{i}")
        if prompt is not None:
            cu.publish_message(content=prompt)
            st.rerun()
