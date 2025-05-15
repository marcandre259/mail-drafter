from mail_drafter.create_draft import gmail_create_draft, gmail_create_draft_reply
from mail_drafter.draft_generator import (
    generate_email_draft,
    generate_email_content_from_audio,
    load_api_keys,
)
from mail_drafter.thread_context import get_thread_context
from mail_drafter.sst import start_recording
from mail_drafter.utility import delete_recording

from typing import Optional


def prepare_content_draft(
    prompt: str, recipient_mail: str, subject: Optional[str] = None, reply: bool = False
):
    if reply:
        if not subject:
            raise Exception("Subject must be provided for a reply")

        thread_messages = get_thread_context(subject)

        thread_formatted_messages = [
            message.format_string() for message in thread_messages
        ]

        prompt += "\nMessage thread context:\n"

        for formatted_message in thread_formatted_messages:
            prompt += f"{formatted_message}\n"

    response = generate_email_content_from_audio(
        "data/live_recording.mp3", api_keys.get("GOOGLE_API_KEY"), text_prompt=prompt
    )

    if subject:
        gmail_create_draft_reply(
            original_subject=subject,
            recipient_email=recipient_mail,
            content=response.get("content"),
        )
    else:
        gmail_create_draft_reply(
            original_subject=response.get("subject"),
            recipient_email=recipient_mail,
            content=response.get("content"),
        )


def prepare_draft(prompt: str, reply: bool = False) -> None:
    response = generate_email_draft(prompt, api_key=api_keys.get("GOOGLE_API_KEY"))

    to = response.get("to")
    subject = response.get("subject")
    content = response.get("content")
    cc = response.get("cc")

    if not cc:
        cc = ""

    if not reply:
        gmail_create_draft(to=to, subject=subject, content=content, cc=cc)
    else:
        gmail_create_draft_reply(
            original_subject=subject, recipient_email=to, content=content
        )


if __name__ == "__main__":
    pass
