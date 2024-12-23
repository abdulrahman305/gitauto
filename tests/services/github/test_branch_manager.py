import pytest
from unittest.mock import patch
from services.github.branch_manager import get_default_branch
from tests.constants import GITHUB_API_URL, OWNER, REPO, TOKEN


@patch('requests.get')
def test_get_default_branch(mock_get):
    # Mock response data
    mock_response = {
        "name": "main",
        "commit": {
            "sha": "abc123"
        }
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [mock_response]

    # Call the function
    default_branch, commit_sha = get_default_branch(OWNER, REPO, TOKEN)

    # Assertions
    assert default_branch == "main"
    assert commit_sha == "abc123"
    mock_get.assert_called_once_with(
        url=f"{GITHUB_API_URL}/repos/{OWNER}/{REPO}/branches",
        headers={'Authorization': f'token {TOKEN}'},
        timeout=10
    )
