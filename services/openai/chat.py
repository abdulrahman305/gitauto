# Third-party imports
# Local imports
from config import OPENAI_MODEL_ID, OPENAI_TEMPERATURE
from utils.handle_exceptions import handle_exceptions

from openai import OpenAI
from openai.types.chat import ChatCompletion
from services.openai.init import create_openai_client
from services.openai.instructions import SYSTEM_INSTRUCTION_FOR_WRITING_PR


@handle_exceptions(raise_on_error=True)
def write_pr_body(input_message: str) -> str:
    """https://platform.openai.com/docs/api-reference/chat/create"""
    client: OpenAI = create_openai_client()
    completion: ChatCompletion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION_FOR_WRITING_PR},
            {"role": "user", "content": input_message},
        ],
        model=OPENAI_MODEL_ID,
        n=1,
        temperature=OPENAI_TEMPERATURE,
    )
    content: str | None = completion.choices[0].message.content
    response: str = content if content else "No response from OpenAI"

    # Check for backticks
    if response[:4] == "```\n":
        response = response[4:]
    if response[:3] == "```":
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]

    # Check for triple quotes
    if response[:4] == '"""\n':
        response = response[4:]
    if response[:3] == '"""\n':
        response = response[3:]
    if response.endswith('"""'):
        response = response[:-3]

    return response
