from .config import DRAFT_MODEL
from ollama import chat
from pydantic import BaseModel
from datetime import datetime
from typing import List
from .message import MailMessage
import json


class ChatEntry(BaseModel):
    author: str
    date_sent: datetime
    enty_content: str


class EmailChat(BaseModel):
    entries: List[ChatEntry]

    def format_chat_for_llm(self) -> str:
        sorted_entries = sorted(self.entries, key=lambda e: e.date_sent)
        formatted = {
            "chat": [
                {
                    "author": e.author,
                    "date_sent": e.date_sent.isoformat(),
                    "content": e.enty_content.strip(),
                    "focus": i == len(sorted_entries) - 1,
                }
                for i, e in enumerate(sorted_entries)
            ],
            "instruction": "Summarize this chat focusing on the last entry, using the previous context.",
        }
        return json.dumps(formatted, indent=2)


def generate_default_chat(message: MailMessage) -> EmailChat:
    assert message.Reply_To is None

    return EmailChat(
        entries=[
            ChatEntry(
                author=message.Sender,
                date_sent=message.Date_Sent,
                enty_content=message.Content,
            )
        ]
    )


def generate_email_chat_with_ollama(message: MailMessage) -> EmailChat:
    assert message.Reply_To is not None

    response = chat(
        model=DRAFT_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract conversation entries from the email reply below. "
                    "Return ONLY a valid JSON array without any extra text. "
                    "Each entry must have:\n"
                    " - author: sender's email\n"
                    " - date_sent: ISO 8601 timestamp\n"
                    " - entry_content: message body without quoted text. Include the greetings at the start and end if there are any.\n\n"
                    f"<mailContent>{message.Content}</mailContent>"
                ),
            }
        ],
        format=EmailChat.model_json_schema(),
    )

    return EmailChat.model_validate_json(response.message.content)
