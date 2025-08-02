import asyncio
from zoneinfo import reset_tzpath

import reflex as rx
from typing import List

from pydantic.v1.datetime_parse import parse_time

from . import ai
from reflex_gpt.models import ChatSession, ChatSessionMessageModel


class ChatMessage(rx.Base):
    message: str
    is_bot: bool = False


class ChatState(rx.State):
    chat_session: ChatSession = None
    did_submit: bool = False
    messages: List[ChatMessage] = []

    @rx.var
    def user_did_submit(self) -> bool:
        return self.did_submit

    def create_new_chat_session(self):
        with rx.session() as db_session:
            obj = ChatSession()
            db_session.add(obj)
            db_session.commit()
            db_session.refresh(obj)
            self.chat_session = obj

    def on_load(self):
        print("Running on load")
        if self.chat_session is None:
            self.create_new_chat_session()

    def clear_and_start_new(self):
        self.chat_session = None
        self.messages = []
        self.create_new_chat_session()
        yield

    def insert_message_to_db(self, content, role='unknown'):
        print("insert message data to db")
        if self.chat_session is None:
            return
        if not isinstance(self.chat_session, ChatSession):
            return
        with rx.session() as db_session:
            data = {
                "session_id": self.chat_session.id,
                "content": content,
                "role": role
            }
            obj = ChatSessionMessageModel(**data)
            db_session.add(obj)  # prepare to save
            db_session.commit()  # actually save

    def append_message_to_ui(self, message, is_bot:bool=False):
        self.messages.append(
            ChatMessage(
                message=message,
                is_bot=is_bot
            )
        )

    def get_gtp_messages(self):
        gtp_messages=[{
            'role': 'system',
            'content': 'You are an expert at creating recipies like an elite chief. Respond in markdown'
        }]
        for chat_message in self.messages:
            role='user'
            if chat_message.is_bot:
                role='system'
            gtp_messages.append({
                'role': role,
                'content': chat_message.message
            })
        return gtp_messages

    async def handle_submit(self, form_data:dict):
        print(form_data)
        user_message = form_data.get('message')
        if user_message:
            self.did_submit = True
            self.append_message_to_ui(user_message, is_bot=False)
            self.insert_message_to_db(user_message, role="user")
            yield
            gtp_messages = self.get_gtp_messages()
            bot_response = ai.get_llm_response(gtp_messages)
            self.did_submit = False
            self.append_message_to_ui(bot_response, is_bot=True)
            self.insert_message_to_db(bot_response, role="system")
            yield