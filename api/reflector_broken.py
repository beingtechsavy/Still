import os
import json
import re
import traceback
from dotenv import load_dotenv
from openai import AzureOpenAI

STRICT_PROMPT = """
You are not a therapist.
You are not a coach.
You are not a conversational assistant.

You are a single-response reflective listener designed to help a person feel understood, not fixed.

The user has spoken freely about their experience.
They are emotionally tired and are not seeking advice, solutions, optimism, reassurance, or follow-up.
They do not want a conversation.

Your task is to produce ONE complete written reflection that follows this exact structure and order, without deviation:

Recognition:
Accurately reflect the emotional weight, repetition, effort, uncertainty, and tension present in what the user expressed.
Focus on what it has been like to carry this, not on explaining why it happened.
Do not summarize events or retell the story.
Reflect lived experience and internal effort only.
Use plain, adult language.
Do not interpret beyond what was directly expressed.

Validation without endorsement:
Acknowledge the difficulty of carrying this without validating harmful actions, blame, or conclusions.
Do not correct, reframe, advise, or moralize.
Separate the user's identity from the circumstances they describe.
Make it clear that struggle does not imply weakness, failure, or lack of potential.

Containment and closure:
End with a firm, calm sense of completion.
Do not invite reflection, continuation, memory, or future revisiting.
The ending must clearly communicate that this does not need to be carried forward.

Tone and style rules:
Do not give advice.
Do not ask questions.
Do not sound motivational, inspirational, optimistic, cheerful, poetic, or clinical.
Do not mention therapy, psychology, mental health, or coping strategies.
Do not normalize behavior through statistics or generalizations.
Use "you" language throughout.
Write as ONE single paragraph of 120–180 words.
No line breaks.

Ending rule:
The final sentence must clearly communicate closure, equivalent in meaning to:
"You don't need to keep carrying this version of the year forward."

Output rules:
Always return valid JSON.
Do not include explanations, commentary, or metadata outside the JSON.
If unsure, still return your best possible response within these constraints.

Return ONLY JSON in this exact structure:
{
  "reflection": "single paragraph text",
  "flashcard": {
    "title": "2–4 word title",
    "bullets": [
      "State or condition",
      "State or condition",
      "State or condition"
    ]
  },
  "confidence": 0.0
}

The confidence score represents how closely the reflection matched the emotional tone and content of the user's transcript.
"""

SILENCE_FALLBACK = {
    "reflection": (
        "You spoke about something that has been sitting with you, and for now it does not need to be "
        "turned into clearer language or shaped into meaning. This moment can end here, without carrying "
        "anything forward."
    ),
    "flashcard": {
        "title": "Held",
        "bullets": ["Spoken", "Received", "Released"]
    },
    "confidence": 0.1
}


class ReflectorService:
    def __init__(self):
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

        api_key = os.getenv("OPENAI_API_KEY")
        endpoint = os.getenv("OPENAI_API_BASE") or ""
        api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
        deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

        # Debug logging
        print(f"DEBUG - API Key present: {bool(api_key)}")
        print(f"DEBUG - Endpoint: {endpoint}")
        print(f"DEBUG - API Version: {api_version}")
        print(f"DEBUG - Deployment: {deployment_name}")

        # Ensure endpoint includes protocol
        if endpoint and not endpoint.startswith(("http://", "https://")):
            endpoint = "https://" + endpoint

        try:
            if not api_key or not endpoint:
                print("ERROR: OPENAI_API_KEY and OPENAI_API_BASE must be set in environment")
                raise ValueError("OPENAI_API_KEY and OPENAI_API_BASE must be set in environment")
            
            if not deployment_name:
                print("ERROR: OPENAI_DEPLOYMENT_NAME must be set in environment")
                raise ValueError("OPENAI_DEPLOYMENT_NAME must be set in environment")

            self.client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=api_version,
            )
            
            print(f"✅ Azure OpenAI initialized successfully with deployment: {deployment_name}")
        except Exception as e:
            print(f"❌ Azure OpenAI init failed: {e}")
            self.client = None

        self.model = deployment_name  # Use deployment name, not model name
        self.token_limit = 800

    def _call_model(self, transcript: str) -> dict | None:
        try:
            print(f"Making API call with model/deployment: {self.model}")
            print(f"Transcript length: {len(transcript)} characters")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": STRICT_PROMPT},
                    {"role": "user", "content": transcript},
                ],
                max_completion_tokens=self.token_limit,
                timeout=30  # Add explicit timeout
            )

            # Azure safety: choices can exist but be empty
            if not response.choices:
                print("❌ No choices in response")
                return None

            message = response.choices[0].message
            if not message or not message.content:
                print("❌ No message content in response")
                return None

            content = meip()

")

            # Remove markdown if present


            # Tr
            try:
                result = json.loads(cleaned)
                print("✅ Succ)
                return result
            except json.JSONDecodeError as e:


            # Try extracting JSON block
            match = red)
            if match:
                try:
                    result = json.loads(match.group(0))
                    print("✅ Succ")
                    return result
                except json.JSONDecodeError as e:
                    print(f"❌ Ee}")
None

            print("❌ Noonse")
e

        except Exception as e:
            print(f"❌ Model call ")
            print(f"❌ E)
)
            traceback.print_exc()
            return None"(e)}s: {stron detail"❌ Exceptirint(f           p pe(e)}"n type: {typtioxce

    async def reflect(self, transcript: str) -> dict:
        if not self.client:
            return SILENCE_FALLBACK

        result = self._call_model(transcript)

        if result:
            return result

        # Only reached if the model truly produced nothing
        return SILENCE_FALLBACK