# flake8: noqa
# Standard imports
from typing import Any

# Third-party imports
from openai.types import shared_params

# Local imports
from services.github.github_manager import get_remote_file_content

FILE_PATH: dict[str, str] = {
    "type": "string",
    "description": "The full path to the file within the repository. For example, 'src/openai/__init__.py'.",
}
OWNER: dict[str, str] = {
    "type": "string",
    "description": "The owner of the repository. For example, 'openai'.",
}
REF: dict[str, str] = {
    "type": "string",
    "description": "The ref (branch) name where the file is located. For example, 'main'.",
}
REPO: dict[str, str] = {
    "type": "string",
    "description": "The name of the repository. For example, 'openai-python'.",
}

GET_REMOTE_FILE_CONTENT: shared_params.FunctionDefinition = {
    "name": "get_remote_file_content",
    "description": "Fetches the content of a file from GitHub remote repository given the owner, repo, file_path, and ref when you need to access the file content to analyze or modify it.",
    "parameters": {
        "type": "object",
        "properties": {
            "owner": OWNER,
            "repo": REPO,
            "file_path": FILE_PATH,
            "ref": REF,
        },
        "required": ["owner", "repo", "file_path", "ref"],
    },
}


def reason_for_modying_diff(why: str, *args: str, **kwargs: str) -> None:
    """When prompted to review a list of diffs, use this function to explain why and what you're going to modify in the given diff before actually modifying it. Have inputs '*args and *kwargs' as Assistant API sometimes adds a token as an input."""
    print(f"\n\nWhy Agent Modifying diffs: {why}\n\n")


WHY: dict[str, str] = {
    "type": "string",
    "description": "Reason for modifying the diff you are currently reviewing.",
}

REASON_FOR_MODYING_DIFF: shared_params.FunctionDefinition = {
    "name": "reason_for_modying_diff",
    "description": "When instructed to review the diffs you've created, if you find out you need to modify a diff, first explain using this function why you are modifying the diffs before you actually modify the diffs in your response. Only argument is 'why' which is a string.",
    "parameters": {
        "type": "object",
        "properties": {"why": WHY},
        "required": ["why"],
    },
}

# Define functions
functions: dict[str, Any] = {
    "get_remote_file_content": get_remote_file_content,
    "reason_for_modying_diff": reason_for_modying_diff,
}
