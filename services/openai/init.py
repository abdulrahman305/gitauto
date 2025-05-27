from config import OPENAI_API_KEY, OPENAI_ORG_ID

from openai import OpenAI


def create_openai_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORG_ID)
