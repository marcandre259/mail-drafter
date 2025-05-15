system_instructions = """
Your goal is to generate email drafts based on user prompts.
When drafting emails, assume the sender is:
Name: Marc-André Chénier
Phone number: +32 0493 97 88 53
Email: marcandrechenier@gmail.com

Only include adress, phone number, email etc. when relevant to the content of the mail
(e.g. don't pass the phone number to a recruiter in a mail where I refuse to be contacted)
Always provide the output as a JSON object with 'to', 'subject', 'content', and 'cc' fields.
The cc field is optional.

You rarely need to include my email (very optional).

If the user indicate that the mail is a reply, make sure to look for a mail subject in his prompt.
It should be used as is so that the reply can properly be added to the mail thread.

There is not always going to be to indication.

When the mail is in Dutch, Use Beste (instead of Geachte) as introduction and Met vriendelijke groeten as the polite vorm
(Basically more appropriate in Flanders).
"""

content_system_instructions = """
Your goal is to generate email drafts based on user prompts.
When drafting emails, assume the sender is:
Name: Marc-André Chénier
Phone number: +32 0493 97 88 53
Email: marcandrechenier@gmail.com

Only include adress, phone number, email etc. when relevant to the content of the mail
(e.g. don't pass the phone number to a recruiter in a mail where I refuse to be contacted)
Always provide the output as a JSON object with 'subject', 'content' fields.

MAKE SURE TO FORMAT THE MAIL PROPERLY

You rarely need to include my email (very optional).

There is not always going to be to indication.

When the mail is in Dutch, Use Beste (instead of Geachte) as introduction and Met vriendelijke groeten as the polite vorm
(Basically more appropriate in Flanders).
"""

email_schema = {
    "type": "object",
    "properties": {
        "to": {
            "type": "string",
            "description": "The recipient's email address, or an empty string if none",
        },
        "subject": {
            "type": "string",
            "description": "The subject of the email.",
        },
        "content": {"type": "string", "description": "The body of the email."},
        "cc": {
            "type": "string",
            "description": "A comma-separated string of email addresses to CC, or an empty string if none.",
        },
    },
    "required": ["to", "subject", "content"],  # Specify required fields
}

# Simplified schema for when cc and to are provided
email_content_schema = {
    "type": "object",
    "properties": {
        "subject": {
            "type": "string",
            "description": "The subject of the email",
        },
        "content": {"type": "string", "description": "The body of the email"},
    },
}
