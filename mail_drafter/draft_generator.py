from google import genai
from google.genai import types
import os
from typing import Optional, List, Dict, Any
import json

from mail_drafter.agent_instructions import (
    system_instructions,
    content_system_instructions,
    email_schema,
    email_content_schema,
)


def load_api_keys(file: str) -> str:
    with open(file, "r") as f:
        api_keys = json.load(f)

    return api_keys


def generate_email_content_from_audio(
    audio_path: str,
    api_key: str,
    text_prompt: str = "Use the information to write a relevant email",
) -> Optional[Dict[str, Any]]:
    try:
        model_name = "gemini-2.5-flash-preview-04-17"
        client = genai.Client(api_key=api_key)

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        # Define the expected JSON schema

        response = client.models.generate_content(
            model=model_name,
            contents=[
                text_prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/mp3",
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=content_system_instructions,
                response_mime_type="application/json",
                response_schema=email_content_schema,  # Use the defined schema
                temperature=0.0,
            ),
        )

        # The API should return valid JSON matching the schema, so direct parsing is safer
        import json

        try:
            email_data = json.loads(response.text)
            return email_data
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from the API response.")
            print("API Response Text:", response.text)
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def generate_email_draft(prompt: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Generates a draft email using the latest Gemini Flash API with a defined schema.

    Args:
        prompt: The prompt describing the content and purpose of the email.

    Returns:
        A dictionary containing the email structure (to, subject, content, cc)
        or None if the generation fails or the output is not in the expected format.
    """
    try:
        model_name = "gemini-2.5-flash-preview-04-17"
        client = genai.Client(api_key=api_key)

        # Define the expected JSON schema

        response = client.models.generate_content(
            model=model_name,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config=types.GenerateContentConfig(
                system_instruction=system_instructions,
                response_mime_type="application/json",
                response_schema=email_schema,  # Use the defined schema
                temperature=0.0,
            ),
        )

        # The API should return valid JSON matching the schema, so direct parsing is safer
        import json

        try:
            email_data = json.loads(response.text)
            return email_data
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from the API response.")
            print("API Response Text:", response.text)
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    from mail_drafter.thread_context import get_thread_context
    from mail_drafter.sst import start_recording

    api_keys = load_api_keys("api_keys.json")

    # email_prompt = "Draft an email to John Doe at john.doe@example.com about the project status meeting next week. The meeting is on Tuesday at 10 AM in Room 3B. Please include Jane Smith in CC at jane.smith@example.com."
    output = start_recording()

    # draft = generate_email_draft(email_prompt, api_key=api_keys.get("GOOGLE_API_KEY"))
    if output:
        audio_path = "data/live_recording.mp3"
        draft = generate_email_content_from_audio(
            audio_path, api_key=api_keys.get("GOOGLE_API_KEY")
        )

    if draft:
        print("Generated Email Draft (with Schema):")
        # print(f"To: {draft.get('to')}")
        print(f"Subject: {draft.get('subject')}")
        # if draft.get("cc"):
        #     print(f"CC: {draft.get('cc')}")
        print("\nContent:")
        print(draft.get("content"))
    else:
        print("Failed to generate email draft (with Schema).")
