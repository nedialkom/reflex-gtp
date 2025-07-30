import asyncio
import reflex as rx
from typing import List

from pydantic.v1.datetime_parse import parse_time

from . import ai

class ChatMessage(rx.Base):
    message: str
    is_bot: bool = False


class ChatState(rx.State):
    did_submit: bool = False
    messages: List[ChatMessage] = []

    @rx.var
    def user_did_submit(self) -> bool:
        return self.did_submit

    def append_message(self, message, is_bot:bool=False):
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
            self.append_message(user_message, is_bot=False)
            yield
            gtp_messages = self.get_gtp_messages()
            bot_response = ai.get_llm_response(gtp_messages)
            self.did_submit = False
            self.append_message(bot_response, is_bot=True)
            yield