from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from dataclasses import dataclass
from typing import List
import base64

from mail_drafter.utility import check_creds

# Example thread id '196ce439a1b065bd'


@dataclass
class MessageContent:
    date: str
    labels: List[str]
    author: str
    subject: str
    content: str

    def format_string(self):
        s = f"""
            Date: {self.date}
            Labels: {self.labels}
            Author: {self.author}
            Subject: {self.subject}
            ---
            Content: {self.content}
            ---
            """
        return s


def get_thread_context(thread_id: str, search: bool = True):
    # thread_id is the actual id if search is false
    creds = check_creds()

    try:
        service = build("gmail", "v1", credentials=creds)

        if search:
            search_query = f'subject:"{thread_id}"'

            messages = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    q=search_query,  # Use quotes for subjects with spaces
                    maxResults=1,  # We only need the first match
                )
                .execute()
            )

            thread_id = messages.get("messages")[0].get("threadId")

        messages = service.users().threads().get(userId="me", id=thread_id).execute()

        message_data = []

        for message in messages.get("messages"):
            if not "DRAFT" in message.get("labelIds"):
                current_labels = message.get("labelIds")

                payload = message.get("payload")
                # A lot of info comes from the email headers
                for header in payload.get("headers"):
                    if header.get("name") == "Date":
                        current_date = header.get("value")
                    elif header.get("name") == "Subject":
                        current_subject = header.get("value")
                    elif header.get("name") == "From":
                        current_author = header.get("value")

                # Try to get the body directly
                body = payload.get("body")
                if body and body.get("data"):
                    current_encoded_content = body.get("data")
                else:
                    # Handle nested parts
                    current_part = payload
                    while current_part.get("parts"):
                        current_part = current_part.get("parts")[0]
                    current_encoded_content = current_part.get("body").get("data")

                current_content = base64.urlsafe_b64decode(
                    current_encoded_content.encode()
                ).decode()

                message_content = MessageContent(
                    date=current_date,
                    labels=current_labels,
                    author=current_author,
                    subject=current_subject,
                    content=current_content,
                )

                message_data.append(message_content)

        return message_data

    except HttpError as e:
        print(f"{e}")
        return None


# Need to convert the MessageContent to a nice string

if __name__ == "__main__":
    # get_thread_context(thread_id="196ce439a1b065bd", search=False)
    output = get_thread_context(thread_id="Aanvraag planning", search=True)

    print(output)
