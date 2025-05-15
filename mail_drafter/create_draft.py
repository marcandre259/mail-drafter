import base64
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from typing import Union, List, Optional

from mail_drafter.utility import check_creds


def gmail_create_draft(
    to: str,
    subject: str,
    content: str,
    cc: Optional[Union[List[str], str]] = None,
):
    """Create and insert a draft email.
     Print the returned draft's message and id.
     Returns: Draft object, including draft id and message meta data.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = check_creds()

    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()

        message.set_content(content)

        message["To"] = to
        message["From"] = "marcandrechenier@gmail.com"
        message["Subject"] = subject
        if cc:
            if isinstance(cc, list):
                cc = ", ".join(cc)
            message["Cc"] = cc

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        draft = (
            service.users().drafts().create(userId="me", body=create_message).execute()
        )

        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        draft = None

    return draft


def gmail_create_draft_reply(
    original_subject: str,
    recipient_email: str,
    content: str,
):
    creds = check_creds()
    try:
        service = build("gmail", "v1", credentials=creds)

        # search_query = (
        #     f'from:{to} subject:"{subject}"'  # Use quotes for subjects with spaces
        # )
        search_query = f'subject:"{original_subject}"'

        thread_messages = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=search_query,  # Use quotes for subjects with spaces
                maxResults=1,  # We only need the first match
            )
            .execute()
        )

        thread_id = thread_messages.get("messages")[-1].get("threadId")
        message_id = thread_messages.get("messages")[-1].get("id")

        message = service.users().messages().get(userId="me", id=message_id).execute()
        payload = message.get("payload")

        # Get subject
        for header in payload.get("headers"):
            if header.get("name") == "Subject":
                original_subject = header.get("value").replace("Re: ", "")

        # Get the actual subject
        message = EmailMessage()
        message.set_content(content)

        message["To"] = recipient_email
        message["From"] = "marcandrechenier@gmail.com"  # Your email address

        # Set the reply subject
        reply_subject = f"Re: {original_subject}"
        message["Subject"] = reply_subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create the draft within the thread using threadId
        create_message_body = {
            "message": {
                "raw": encoded_message,
                "threadId": thread_id,  # Associate the draft with the thread
            }
        }

        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message_body)
            .execute()
        )

        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        draft = None

    return draft


if __name__ == "__main__":
    gmail_create_draft_reply(
        "Aanvraag planning",
        "euroluc@telenet.be",
        "This is a test",
    )

    # to = "abc@gmail.com"
    # subject = "test"
    # content = "Hello"
    # cc = ["katrien@hotmail.com", "mc@gmail.com"]
    # gmail_create_draft(to=to, subject=subject, content=content, cc=cc)

    # output = (
    #     service.users()
    #     .messages()
    #     .list(userId="me", maxResults=10, threadId="L4SDeYf3ok-9NAS8fBLxSw")
    #     .execute()
    # )

    # subject_text = "Aanvraag planning tweejaarlijks onderhoud warmtepomp"
    # sender_email = "marcandrechenier@gmail.com"

    # search_query = f'from:{sender_email} subject:"{subject_text}"'  # Use quotes for subjects with spaces

    # results = (
    #     service.users()
    #     .messages()
    #     .list(
    #         userId="me",
    #         q=search_query,  # Use quotes for subjects with spaces
    #         maxResults=1,  # We only need the first match
    #     )
    #     .execute()
    # )

    # thread = service.users().threads().get(userId="me", id=thread_id).execute()

    # print()

    # mail = (
    #     service.users()
    #     .messages()
    #     .get(
    #         userId="me",
    #         id=thread.get("messages")[1].get("id"),
    #         format="metadata",
    #         metadataHeaders=["Message-ID", "References"],
    #     )
    #     .execute()
    # )

    # mail_headers = mail.get("payload").get("headers")

    # for header in mail_headers:
    #     header_value = header.get("value")
    #     if header.get("name") == "References":
    #         mail_reference = header_value
    #     elif header.get("name") == "Message-ID":
    #         mail_id = header_value

    # decoded_text = base64.urlsafe_b64decode(
    #     mail.get("payload").get("body").get("data")
    # ).decode("utf-8")
    # print(output)
